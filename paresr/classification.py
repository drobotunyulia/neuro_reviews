import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy
from sklearn.preprocessing import LabelEncoder

MODEL_DIR = "./model"
LABELS_COUNT = 3

def eval_net(reports, model, tokenizer, le):
  results = []
  for report in reports:
    tokenized_input = tokenizer(report, return_tensors='pt', truncation=True, max_length=512)
    input_ids = tokenized_input['input_ids']
    attention_mask = tokenized_input['attention_mask']

    model.eval()
    with torch.no_grad():
        logits = model(input_ids, attention_mask=attention_mask).logits

    quest_label = torch.argmax(logits, dim=1).item()
    pred_class = le.classes_[quest_label]

    results.append(pred_class)
  return results

imported_model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, num_labels=LABELS_COUNT)
imported_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
imporeted_label_encoder = LabelEncoder()
imporeted_label_encoder.classes_ = numpy.load('./model/classes.npy', allow_pickle=True)


def load_data():
  # Example evaluate
  print(eval_net(["Спасибо", "Плохо"], imported_model, imported_tokenizer, imporeted_label_encoder))
