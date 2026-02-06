import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from time import time
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.decomposition import PCA
import seaborn as sns

from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score

#################################################################################################
# LOAD DATA
#################################################################################################

train_csv = "fashion-mnist_train.csv"
test_csv = "fashion-mnist_test.csv"

train_df = pd.read_csv(train_csv)
test_df = pd.read_csv(test_csv)

# Pixel features
X_pixels_train = train_df.drop(columns=["label"]).values.astype(np.float32)
y_train = train_df["label"].values.astype(int)
X_pixels_test = test_df.drop(columns=["label"]).values.astype(np.float32)
y_test = test_df["label"].values.astype(int)

# Normalize pixel features to [0,1]
X_pixels_train /= 255.0
X_pixels_test /= 255.0


#################################################################################################
# TRAIN/VALIDATION SPLIT
#################################################################################################

X_tr, X_val, y_tr, y_val = train_test_split(
    X_pixels_train, y_train, test_size=5000, random_state=0, stratify=y_train
)


#################################################################################################
# FIND THE BEST HYPERPARAMETERS FOR THE DATASET
#################################################################################################

train_pool = Pool(X_tr, y_tr)
val_pool = Pool(X_val, y_val)

# compare these three tree depths
depths = [4,6,8]
learning_rates = [0.03, 0.1]
l2_regs = [1.0, 3.0, 5.0]
iterations_fixed = 200

# # Test Set (for testing the code faster)
# depths = [6]
# learning_rates = [0.1]
# l2_regs = [3.0]
# iterations_fixed = 100

best_val_acc = -np.inf
best_params = None

for depth in depths:
    for lr in learning_rates:
        for l2 in l2_regs:
            print(f"Training: depth={depth}, lr={lr}, l2={l2}", flush=True) # Progress check
            params = {
                "loss_function": "MultiClass",
                "eval_metric": "Accuracy",
                "iterations": iterations_fixed,
                "learning_rate": lr,
                "depth": depth,
                "l2_leaf_reg": l2,
                "random_seed": 0,
                "bootstrap_type": "Bernoulli",
                "subsample": 0.8, 
                "verbose": False,
                "early_stopping_rounds": 40,
                "use_best_model": True,
            }
            # Crate the model
            model = CatBoostClassifier(**params)
            # Record the time it takes to train
            start_time = time()
            model.fit(train_pool, eval_set=val_pool, verbose=False)
            end_time = time() - start_time
            y_val_pred = model.predict(val_pool)
            val_acc = accuracy_score(y_val, y_val_pred)

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_params = params

print("\nBest Hyperparameters: ")
print(best_params)
print(f"Best Validation Accuracy = {best_val_acc:.4f}")

#################################################################################################
# 5-FOLD CROSS-VALIDATION USING BEST HYPERPARAMETERS
#################################################################################################


print("\n===============================")
print("===== 5-Fold Cross-Validation =====")

kf = KFold(n_splits=5, shuffle=True, random_state=0)

cv_acc_scores = []
cv_train_times = []

for fold, (train_idx, val_idx) in enumerate(kf.split(X_pixels_train)):
    print(f"Fold {fold + 1}...")

    X_tr_fold = X_pixels_train[train_idx]
    y_tr_fold = y_train[train_idx]
    X_val_fold = X_pixels_train[val_idx]
    y_val_fold = y_train[val_idx]

    model_cv = CatBoostClassifier(**best_params)

    # ---- Time training ----
    start_time = time()
    model_cv.fit(X_tr_fold, y_tr_fold, verbose=False)
    elapsed = time() - start_time

    cv_train_times.append(elapsed)

    # ---- Accuracy ----
    y_pred_fold = model_cv.predict(X_val_fold)
    acc = accuracy_score(y_val_fold, y_pred_fold)
    cv_acc_scores.append(acc)

    print(f"  Fold Acc = {acc:.4f}, Train Time = {elapsed:.2f}s")

print("\n===== CV Summary =====")
print(f"Mean CV Accuracy = {np.mean(cv_acc_scores):.4f}")
print(f"CV Accuracy Std  = {np.std(cv_acc_scores):.4f}")
print(f"Mean Train Time  = {np.mean(cv_train_times):.2f}s")
print(f"Train Time Std   = {np.std(cv_train_times):.2f}s\n")

#################################################################################################
# TRAIN MODELS USING THE BEST HYPERPARAMETER CONFIGURATION
#################################################################################################

# 5 models with different # of trees
iterations_arr = [50, 100, 200, 400, 800]
train_errors = []
val_errors = []
test_errors = []

print("\n===============================")
print("===== Error of each model =====")
# Train these 5 models with different # of trees
for iter in iterations_arr:
    params = best_params.copy()

    # change the values in the hyperparameter configuration and create a new CatBoost model
    params["iterations"] = iter
    params.pop("early_stopping_rounds", None)
    params["use_best_model"] = False
    model = CatBoostClassifier(**params)
    
    # train the model
    model.fit(train_pool, eval_set=val_pool, verbose=False)

    # Predictions on training, validation, and test data
    y_train_pred = model.predict(train_pool)
    y_val_pred = model.predict(val_pool)
    y_test_pred = model.predict(X_pixels_test)

    # Calculate accuracies based on the predictions
    train_acc = accuracy_score(y_tr, y_train_pred)
    val_acc = accuracy_score(y_val, y_val_pred)
    test_acc = accuracy_score(y_test, y_test_pred)

    # Convert accuracy to error, append them into the array
    train_errors.append((1-train_acc) * 100)
    val_errors.append((1-val_acc) * 100)
    test_errors.append((1-test_acc) * 100)

    # Print out the error result of each model
    print(f"{iter} trees: Train error {train_errors[-1]:.2f}% | Val error {val_errors[-1]:.2f}% | Test error {test_errors[-1]:.2f}%")

# Find the best test error (min)
best_test_error_idx = int(np.argmin(test_errors))
best_iter = iterations_arr[best_test_error_idx]
best_test_error = test_errors[best_test_error_idx]

print(f"\nBest Test Error = {best_test_error:.2f}% at {best_iter} trees")


#################################################################################################
# PLOT: ERROR VS # OF TREES
#################################################################################################

plt.figure(figsize=(8,6))
plt.plot(iterations_arr, train_errors, 'b-', linewidth=2, label='Train Error')
plt.plot(iterations_arr, val_errors, 'r-', linewidth=2, label='Val Error')
plt.plot(iterations_arr, test_errors, 'g-', linewidth=2, label='Test Error')
plt.xlabel('Number of Trees', fontsize=12)
plt.ylabel('Error(%)', fontsize=12)
plt.title('Error vs Trees (Fashion-MNIST)', fontsize=14)
plt.legend()
plt.grid(True)
plt.savefig("part3_classification_error_vs_trees.png", dpi=300)


#################################################################################################
# MODEL TRAINING USING THE BEST ITERATION
#################################################################################################

# use the best hyperparameters from part 3
params = best_params.copy()
# use the best number of trees from part 4
params["iterations"] = best_iter
params["early_stopping_rounds"] = 40
params["use_best_model"] = True

# Create the model
model = CatBoostClassifier(**params)

# Record the training time
start_time = time()
model.fit(train_pool, eval_set=val_pool, verbose=False)
end_time = time() - start_time

# Predictions on training, validation, and test data
y_train_pred = model.predict(train_pool)
y_val_pred = model.predict(val_pool)
y_test_pred = model.predict(X_pixels_test)

# Calculate the final accuracies and error
train_acc = accuracy_score(y_tr, y_train_pred)
val_acc = accuracy_score(y_val, y_val_pred)
test_acc = accuracy_score(y_test, y_test_pred)
test_error = (1-test_acc) * 100

# Print the result
print("\n===============================")
print("========= Final Model =========")
print(f"Train Accuracy: {train_acc:.4f}")
print(f"Validation Accuracy: {val_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")
print(f"Test Error: {test_error:.2f}%")
print(f"Training Time: {end_time:.1f}s")


#################################################################################################
# PLOT OF CONFUSION MATRIX
#################################################################################################

cm = confusion_matrix(y_test, y_test_pred)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,7))
labels = ["T-shirt","Trouser","Pullover","Dress","Coat",
          "Sandal","Shirt","Sneaker","Bag","Ankle boot"]

# Plot 1: Raw confusion matrix with counts
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1,
            xticklabels=labels, yticklabels=labels)
ax1.set_xlabel('Predicted Label', fontsize=12)
ax1.set_ylabel('True Label', fontsize=12)
ax1.set_title('Raw Confusion Matrix', fontsize=13)

# Plot 2: Normalized confusion matrix
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
sns.heatmap(cm_norm, annot=True, fmt='.2%', cmap='Blues', ax=ax2,
            xticklabels=labels, yticklabels=labels)
ax2.set_xlabel('Predicted Label', fontsize=12)
ax2.set_ylabel('True Label', fontsize=12)
ax2.set_title('Normalized Confusion Matrix', fontsize=13)

# Save confusion matrix plot
plt.tight_layout()
plt.savefig("part3_classification_confusion_matrix.png", dpi=300)
plt.close()


#################################################################################################
# PCA
#################################################################################################

pca = PCA(n_components=50, random_state=0)

# Apply PCA to train, validation, and test
X_tr_pca = pca.fit_transform(X_tr)
X_val_pca = pca.transform(X_val)
X_test_pca = pca.transform(X_pixels_test)

# copy the best parameter configuration
params_pca = best_params.copy()
params_pca["iterations"] = 200
params_pca["early_stopping_rounds"] = 40
params_pca["use_best_model"] = True

# Create the PCA model
model_pca = CatBoostClassifier(**params_pca)
model_pca.fit(X_tr_pca, y_tr, eval_set=(X_val_pca, y_val), verbose=False)

# Calculate the accuracy and error
y_test_pca = model_pca.predict(X_test_pca)
acc_pca = accuracy_score(y_test, y_test_pca)
error_pca = (1-acc_pca) * 100

print("\n===============================")
print("========== PCA Model ==========")
print(f"Test Accuracy: {acc_pca:.4f}")
print(f"Test Error: {error_pca:.2f}%")


#################################################################################################
# RELEVANT FEATURE
#################################################################################################
# Find the top 10 most important pixels

# Get the importance of each pixel
importances = model.get_feature_importance(train_pool)
# only keep the first 10 indices from largest to smallest
idx = np.argsort(importances)[::-1][:10]

plt.figure(figsize=(10,6))
plt.bar(range(10), importances[idx])
plt.xticks(range(10), idx, rotation=45)
plt.title('Top 10 Pixel Importances')
plt.tight_layout()
plt.savefig("part3_classification_feature_importance.png", dpi=300)
plt.close()


#################################################################################################
# SAVE RESULT
#################################################################################################
results_filename = f"part3_results_catboost.txt"
with open(results_filename, 'w') as f:
    f.write("===============================\n")
    f.write("======= Best Parameters =======\n")
    f.write(f"{best_params}\n\n")
    f.write("===============================\n")
    f.write("===== Best Number of Tree =====\n")
    f.write(f"{best_iter}\n\n")
    f.write("===============================\n")
    f.write("========= Final Model =========\n")
    f.write(f"Train Accuracy     : {train_acc:.4f}\n")
    f.write(f"Validation Accuracy: {val_acc:.4f}\n")
    f.write(f"Test Accuracy      : {test_acc:.4f}\n")
    f.write(f"Test Error         : {test_error:.2f}%\n\n")
    f.write("===============================\n")
    f.write("========== PCA Model ==========\n")
    f.write(f"Test Accuracy: {acc_pca:.4f}\n")
    f.write(f"Test Error   : {error_pca:.2f}%")

print(f"Saved results: {results_filename}")