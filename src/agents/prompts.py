
PROMPT_VERSION = "v1.0"

FEATURE_SELECTION_PROMPT = """
You are a reasoning agent tasked with selecting user features that are most relevant for predicting whether a user will use a specific product. You may receive messages that provide information about the product, its features, the target audience and expert guide (if any).

You will be provided with the following information:
- Product Name: {product_name}
- Product Description: {product_description}
- Target Audience (Best Fit): {user_portrait}
- User Feature Data:
{user_features}

Your task is to analyze the above information, understand the domain expert's request and follow a step-by-step reasoning process to identify the most relevant user features for this product. The features should come from the user feature data input, do not modify or generate new features.

In final, give a list of user features that are most relevant to predicting product usage. 
"""



SYSTEM_PROMPT_EXTRACT_DATA_AGENT = (
    "You are a data extraction agent that can extract feature data based on the provided messages.\n"
    "You will be given messages reasoning about which features should be selected for training a machine learning model.\n"
    "From the reasoning message, extract a dictionary containing the sfeature data. Only extract the features in the messages; do not generate any new features.\n\n"
    "The output should be a dictionary with the following structure:\n"
    "{\n"
    '    "features": {\n'
    '        "feature_name_1": "feature_description_1",\n'
    '        "feature_name_2": "feature_description_2",\n'
    "        ...\n"
    "    }\n"
    "}\n"
)

EXPLAIN_MODEL_PROMPT = """
You are an expert at explaining machine learning models to non-technical audiences.
You will be given additional information about a banking product, a list of features, and a tree based model.
Your task is to clearly explain how the model works in simple terms for a banking product owner who wants to understand how customer characteristics influence product usage.

Your explanation should:
- Break down each part of the tree using plain, easy-to-understand language.
- Provide a final summary highlighting the key insights and how they can inform product decisions.
- Jump straight to the point.

Product Information:
- Product Name: {product_name}
- Product Description: {product_description}

Features:
{feature_data}

Target Prediction:
- Not interacted = Customer is likely to use the product
- Interacted = Customer is unlikely to use the product

Decision Tree:
{tree_graph_text}

Be concise and focus on what matters to a banking product owner—how the model makes decisions and what customer traits drive product usage. Do not give any suggestions. If the user asks, help them answer their questions based on the provided information and the decision tree model. 
"""

LOCAL_EXPLAIN_MODEL_PROMPT = """
You are a local explanation agent working with a predictive model for a banking product.
The model estimates the probability (between 0 and 1) that a given user will use this specific banking product.

You will be given:

• User Feature Metadata:
{feature_metadata}

Product Feature Metadata:
{product_feature_metadata}

Product Category:
{product_category}

• Model Information:
- Feature Importance Scores (each feature's contribution to the model overall):
{feature_importances}
- Feature Values for this specific user:
{feature_data}
- Predicted Label (True/False): {predicted_label}
- Model Predicted Probability (likelihood): {likelihood}

Your task is to provide TWO explanations:

1. DETAILED EXPLANATION (3-5 sentences):
    Explain why the model arrived at this prediction for the given user, focusing on:
    - What type of user this is based on their characteristics
    - What type of product this is and its purpose
    - Why this user is likely or unlikely to match with this product based on key features

2. SHORT SUMMARY (1 sentence):
    A concise version of the detailed explanation highlighting only the most critical factors.

Be clear, focus on the instance-level decision, and avoid technical jargon in both explanations.
"""
