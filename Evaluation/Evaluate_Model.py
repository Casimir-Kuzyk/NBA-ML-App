from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import numpy as np

#learn about these evaluation metrics here:
# https://www.analyticsvidhya.com/blog/2020/08/bias-and-variance-tradeoff-machine-learning/?utm_source=blog&utm_medium=precision_and_recall
# https://www.analyticsvidhya.com/blog/2020/09/precision-recall-machine-learning/ 
# https://www.v7labs.com/blog/f1-score-guide#:~:text=F1%20score%20is%20a%20machine%20learning%20evaluation%20metric%20that%20measures,prediction%20across%20the%20entire%20dataset. 
# https://www.analyticsvidhya.com/blog/2020/06/auc-roc-curve-machine-learning/#:~:text=A.%20AUC%20ROC%20stands%20for,summary%20of%20the%20ROC%20curve. 

def evaluate_model(model, val_data, val_labels):
    val_loss, val_accuracy = model.evaluate(val_data, val_labels)
    print(f"Validation accuracy: {val_accuracy * 100:.2f}%")

        # Predict probabilities
    val_prob = model.predict(val_data)
    
    # Convert probabilities into binary outputs
    val_pred = np.where(val_prob > 0.5, 1, 0)
    
    # Calculate metrics
    precision = precision_score(val_labels, val_pred)
    recall = recall_score(val_labels, val_pred)
    f1 = f1_score(val_labels, val_pred)
    roc_auc = roc_auc_score(val_labels, val_prob)  # note that roc_auc_score takes the probabilities, not the binary predictions

    print(f"Validation Precision: {precision * 100:.2f}%")
    print(f"Validation Recall: {recall * 100:.2f}%")
    print(f"Validation F1-Score: {f1 * 100:.2f}%")
    print(f"Validation ROC-AUC: {roc_auc * 100:.2f}%")