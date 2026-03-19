# Domain Adapted AI Assistant

This project demonstrates domain adaptation using LoRA fine-tuning to improve responses for domain-specific questions. The system extends a basic GenAI pipeline by adapting the model using an instruction dataset.

---

## Pipeline

User → Streamlit → FastAPI → Fine-tuned Model

---

## Domain Task

The system is designed to answer computer science questions (mainly operating systems concepts) with clearer and more structured explanations.

---

## Instruction Dataset

An instruction dataset was created using question-answer pairs related to operating systems topics. This dataset helps guide the model to produce more consistent and domain-specific responses.

File:
- instructions.json

---

## Adaptation Method

We used LoRA (Low-Rank Adaptation) with the PEFT library to fine-tune the model efficiently without retraining the entire model.

Training script:
- training/train_lora.py

---

## Steps

### Install dependencies
pip install -r requirements.txt

### Train model
python training/train_lora.py

### Start API
uvicorn app.api:app --reload

### Run Streamlit
streamlit run app/streamlit_app.py

---

## Evaluation

The system was tested using multiple queries before and after adaptation.

After applying domain adaptation:
- Responses became more structured  
- Answers were more relevant to the domain  
- Less generic responses  

---

## Team Contributions

### Ibrahim Alborno (50%)
- Instruction dataset creation and expansion  
- LoRA fine-tuning implementation  
- Backend integration using FastAPI  
- Evaluation of adapted model  

### Team Member (50%)
- Streamlit UI development  
- System testing and debugging  
- Prompt refinement  
- Project organization  

---

## Notes

This project shows how domain adaptation can improve a GenAI system while keeping the training process efficient using LoRA.
