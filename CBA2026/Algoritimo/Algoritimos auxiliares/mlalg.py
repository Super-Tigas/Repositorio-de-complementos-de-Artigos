from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np
import matplotlib.pyplot as plt

def machinelearning(X,y):

    X=np.asanyarray(X)
    y=np.asanyarray(y)
    
    model= XGBRegressor(
        objective='reg:squarederror',
        n_estimators=1000,
        learning_rate=0.01,
        max_depth=5,
        tree_method='hist'
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train,y_train)
    y_pred=model.predict(X_test)
    
    return model,y_test,y_pred

def metrics(y_test,y_pred):

    med_error=mean_absolute_error(y_test,y_pred)
    r2_metric=r2_score(y_test,y_pred)

    

    return med_error,r2_metric

def plot_results(y_true, y_pred):
    plt.figure(figsize=(10, 6))
    plt.plot(y_true.values if hasattr(y_true, 'values') else y_true, label='Dados Reais (NASA)', color='blue', alpha=0.6)
    plt.plot(y_pred, label='Previsão XGBoost', color='red', linestyle='--')
    plt.title('Comparação: Degradação Real vs. Prevista')
    plt.xlabel('Amostras de Teste (Ciclos)')
    plt.ylabel('Capacidade (Ah)')
    plt.legend()
    plt.grid(True)
    plt.show()


   