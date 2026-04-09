# EECS4312_W26_SpecChain

## instructions:
Please update to include: 
- App name: 
- Data collection method
- Original dataset
- Final cleaned dataset
- Exact commands to run pipeline

# example
Application: [Headspace]

Dataset:
- reviews_raw.jsonl contains the collected reviews.
- reviews_clean.jsonl contains the cleaned dataset.
- The cleaned dataset contains 3861 reviews.

Repository Structure:
- data/ contains datasets and review groups
- personas/ contains persona files
- spec/ contains specifications
- tests/ contains validation tests
- metrics/ contains all metric files
- src/ contains executable Python scripts
- reflection/ contains the final reflection

How to Run:
Note: My run_all.py script should the only script that is needed to run the automated pipeline. I used groq API with a key that I saved into my environment. There are a multitude of different pip installs I needed to do, I am unsure if you will be required to install these as well. These include: sentence-transformers scikit-learn groq, nltk, num2words and google-play-scrapper. 
1. python src/00_validate_repo.py
2. python src/run_all.py
3. Open metrics/metrics_summary.json for comparison results

