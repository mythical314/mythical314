# Catboost Study

Collaborators: Andrew Feng, Krish Sarkar, Haofeng Mei

This project is an analysis of a modern machine learning model; a unique gradient boosting algorithm called Catboost. It's a variation of an ensemble tree model that's useful for fitting both regression and classification datasets. The functionality of the code included in this project is as follows:

- Mean Predictor: For the regression dataset, we used the mean predictor as a control to compare the root mean square error (RMSE) of a simplistic fit to that of the CatBoost algorithm.
- Linear Predictor: We used a standard linear regression as a more reasonable baseline for comparing the CatBoost algorithm to a model that actually learns a trend from given data.
- Catboost Hyperparameter Study: We studied many different combinations of hyperparameter values (number of trees, tree depth, learning rate, etc.) in order to attempt to minimize RMSE and form a conclusion based on the results.
- PCA Study: We also ran these algorithms on the same datasets with PCA applied to them, in order to see how feature selection impacts the error.

Running this code locally requires having Python, jupyter, the Catboost module, and the sklearn module installed. You will also need to have the Fashion-MNIST and California Housing datasets in the same directory- these can be found at the following links:

- https://www.kaggle.com/datasets/zalando-research/fashionmnist (get fashion-mnist_test.csv and fashion-mnist_train.csv)
- https://www.kaggle.com/code/hassaan2580/california-housing-dataset (get housing.csv)

The results of this study are included within this directory, in a pdf report that I compiled.

This was a challenging project- I'm thankful to my collaborators for working with me to produce these results. Please let me know if you have feedback!
