WORKFLOW_EXAMPLE_METADATA = [
    {
        "name": "AI_Automated_HR_Workflow_for_CV_Analysis_and_Candidate_Evaluation",
        "description": """This workflow automates the process of handling job applications by extracting relevant information from submitted CVs, analyzing the candidate's qualifications against a predefined profile, and storing the results in a Google Sheet. Here’s how it operates:

Data Collection and Extraction:

The workflow begins with a form submission (On form submission node), which triggers the extraction of data from the uploaded CV file using the Extract from File node.
Two informationExtractor nodes (Qualifications and Personal Data) are used to parse specific details such as educational background, work history, skills, city, birthdate, and telephone number from the text content of the CV.
Processing and Evaluation:

A Merge node combines the extracted personal and qualification data into a single output.
This merged data is then passed through a Summarization Chain that generates a concise summary of the candidate’s profile.
An HR Expert chain evaluates the candidate against a desired profile (Profile Wanted), assigning a score and providing considerations for hiring.
Finally, all collected and processed data including the evaluation results are appended to a Google Sheets document via the Google Sheets node for further review or reporting purposes [[9]].
""",
        "file_path": "example_workflow/AI_Automated_HR_Workflow_for_CV_Analysis_and_Candidate_Evaluation.json"
    },
    {
        "name": "CV_Screening_with_OpenAI",
        "description": """This workflow automates the resume screening process using OpenAI for analysis. It provides a matching score, a summary of candidate suitability, and key insights into why the candidate fits (or doesn’t fit) the job.
Retrieve Resume: The workflow downloads CVs from a direct link (e.g., Supabase storage or Dropbox).
Extract Data: Extracts text data from PDF or DOC files for analysis.
Analyze with OpenAI: Sends the extracted data and job description to OpenAI to:
Generate a matching score.
Summarize candidate strengths and weaknesses.
Provide actionable insights into their suitability for the job.
""",
        "file_path": "example_workflow/CV_Screening_with_OpenAI.json"
    },    
    {
        "name": "CV_Resume_PDF_Parsing_with_Multimodal_Vision_AI",
        "description": """Our candidate's CV/Resume is a PDF downloaded via Google Drive for this demonstration.
The PDF is then converted into an image PNG using a tool called Stirling PDF. Since the hidden prompt has a white font color, it is is invisible in the converted image.
The image is then forwarded to a Basic LLM node to process using our multimodal model - in this example, we'll use Google's Gemini 1.5 Pro.
In the Basic LLM node, we'll need to set a User Message with the type of Binary. This allows us to directly send the image file in our request.
The LLM is now immune to the hidden prompt and its response is has expected.""",
        "file_path": "example_workflow/CV_Resume_PDF_Parsing_with_Multimodal_Vision_AI.json"
    }
]