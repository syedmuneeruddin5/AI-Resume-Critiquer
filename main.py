import streamlit as st
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
from weasyprint import HTML,CSS
from weasyprint.text.fonts import FontConfiguration
import markdown_it

import os
from io import BytesIO
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse
from sseclient import SSEClient
import requests
import json

def get_job_description():

    industries = [
        "Aerospace & Defense",
        "Agriculture & Farming",
        "Architecture & Urban Planning",
        "Artificial Intelligence & Machine Learning",
        "Arts & Design",
        "Automotive",
        "Biotechnology",
        "Blockchain & Cryptocurrency",
        "Construction",
        "Consulting",
        "Cybersecurity",
        "E-commerce",
        "Education",
        "Energy (Oil & Gas)",
        "Engineering",
        "Environmental Services",
        "Event Planning",
        "Fashion & Apparel",
        "Fitness & Wellness",
        "Food & Beverage",
        "Government & Public Administration",
        "Healthcare",
        "Hospitality & Tourism",
        "Human Resources",
        "Insurance",
        "Legal Services",
        "Manufacturing",
        "Marketing & Advertising",
        "Mental Health & Counseling",
        "Nonprofit & Social Services",
        "Pharmaceuticals",
        "Publishing",
        "Real Estate",
        "Renewable Energy",
        "Retail",
        "Scientific Research & Development",
        "Space Exploration",
        "Sports & Recreation",
        "Supply Chain & Procurement",
        "Technology",
        "Telecommunications",
        "Transportation & Logistics",
        "Veterinary Services"
    ]

    job_industry = st.selectbox("Job Industry (Optional)", industries, index=None, accept_new_options=True)
    job_role = st.text_input("Job Role (Optional)")

    return {"job_industry":job_industry,"job_role":job_role}

def setup_model(default_open_router_model="DeepSeek: R1 0528 (free)", default_ollama_model="gemma3:4b"):
    llm_provider = st.selectbox("Choose a LLM Provider", ("Open Router", "Ollama"), index=0)

    if llm_provider == "Open Router":

        open_router_key = st.text_input("Open Router Key", value=(os.getenv("OPEN_ROUTER_API_KEY")), type="password", key="raw_open_router_key")

        if not st.session_state.first_run:
            if check_api_connection_open_router(st.session_state.raw_open_router_key) is not True:
                    st.error(f"API Connection Failed : {check_api_connection_open_router(st.session_state.raw_open_router_key)["message"]}")

        else:
            st.session_state.first_run = False

        if os.getenv("OPEN_ROUTER_API_KEY"):
            st.caption("If no key provided, it will use .env key")
        else:
            st.caption("You can generate your own API key by creating an OpenRouter Account")

        models = get_free_models_openrouter()
        models_name = [i["name"] for i in models]
        models_id = [i["id"] for i in models]

        default_model_index = models_name.index(default_open_router_model) if default_open_router_model in models_name else 0

        model = st.selectbox("Choose a Model",models_id, format_func=lambda m: models_name[models_id.index(m)], index=default_model_index)

        st.session_state.model_details = {"llm_provider":llm_provider, "api_key": open_router_key, "model": model}

    elif llm_provider == "Ollama":

        base_url = st.text_input("Base URL", value="http://localhost:11434/")

        if check_ollama_connection(base_url):
            models = get_ollama_models(base_url)

            default_model_index = models.index(default_ollama_model) if default_ollama_model in models else 0

            model = st.selectbox("Choose a Model", models, index=default_model_index)

            st.session_state.model_details = {"llm_provider": llm_provider, "base_url": base_url, "model": model}

        else:
            st.button("Reconnect")

def check_api_connection_open_router(open_router_key):
    url = "https://openrouter.ai/api/v1/credits"

    headers = {"Authorization": f"Bearer {open_router_key}"}

    response = requests.get(url, headers=headers)

    if "error" in response.json():
        return {"status":"error", "code":response.json()["error"]["code"], "message":response.json()["error"]["message"]}
    else:
        return True

def get_free_models_openrouter():

    models = []

    url = "https://openrouter.ai/api/v1/models"

    response = requests.get(url)

    if response.status_code == 200:
        for model in response.json()["data"]:
            if float(model["pricing"]["prompt"]) == 0 and float(model["pricing"]["completion"]) == 0:
                models.append({"name":model["name"], "id":model["id"]})

    else:
        st.warning("Connection Not Established. Recheck API KEY")

    return models

def check_ollama_connection(base_url):

    endpoint = "/api/tags"
    url = urljoin(base_url, endpoint)

    try:
        response = requests.get(url)

        if "error" in response.json():
            st.error(response.json()["error"])
            return False

    except requests.exceptions.ConnectionError:
        st.error("Please start the Ollama server using : ollama serve")
        st.caption("If the website is running online, it may not work. Clone the code and run locally to use Ollama")
        return False

    return True

def get_ollama_models(base_url):

    endpoint = "/api/tags"
    url = urljoin(base_url, endpoint)

    models = []

    response = requests.get(url)

    if "error" not in response.json():
        data = response.json()["models"]

        for model in data:
            models.append(model["model"])
        return models

    else:
        st.error(response.json()["error"])

st.cache_data(ttl=120)
def extract_text_from_file(source):
    if source.type == 'application/pdf':

        file_stream = BytesIO(source.getvalue())
        doc_stream = DocumentStream(name="my_doc.pdf", stream=file_stream)

        converter = DocumentConverter()
        doc = converter.convert(doc_stream).document
        return doc.export_to_markdown()

    else:
        return source.read().decode('utf-8')

def generate_analysis(resume_content, model_details, job_industry=None, job_role=None):

    prompt = f"""
    Analyze a resume and provide actionable insights based on the job role specified. Here are the details for the analysis:
    {f"- Industry: {job_industry.strip().title()}\n" if job_industry else ""}{f"- Job Role: {job_role.strip().title()}" if job_role else ""}
    - Resume Content: {resume_content}

    ---

    Start with a title.
    The feedback should be structured to include the following sections:
    1. Strengths: Highlight the strong points of the resume.
    2. Areas for Improvement: Identify sections that need enhancement.
    3. Alignment with Job Role: Discuss how well the resume matches the requirements of the job role.
    4. ATS Compatibility: Evaluate whether the resume is ATS-friendly.
    5. Recommendations: Provide specific suggestions to improve the resume.

    ---

    Please ensure that the feedback is clear, actionable, and tailored to the individual’s experience and the job role in question. Avoid generic advice and focus on personalized insights that will help the candidate strengthen their application.

    ---

    Example of a feedback structure:

    ##Strengths:
    - [List strengths here]

    ##Areas for Improvement:
    - [List areas for improvement here]

    ##Alignment with Job Role:
    - [Discuss alignment here]

    ##ATS Compatibility:
    - [Discuss ATS compatibility here]

    ##Recommendations:
    - [Provide recommendations here]

    """

    st.session_state.messages = [
        {"role": "system",
         "content": "You are a seasoned career coach with over 15 years of experience in guiding individuals through their job application processes. Your expertise lies in analyzing resumes to ensure they align with specific job roles and recommending actionable insights."},
        {"role": "user", "content": prompt}
    ]

    if model_details["llm_provider"] == "Open Router":
        analysis = generate_open_router_response(st.session_state.messages, model_details)

    if model_details["llm_provider"] == "Ollama":
        analysis = generate_ollama_response(st.session_state.messages, model_details)

    if analysis:
        st.session_state.messages.append({"role": "assistant", "content": analysis})
        return {"response": analysis, "messages" : st.session_state.messages}
    
    else:
        return False

def generate_open_router_response(messages,model_details, stream=False):

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_details['api_key']}",
    }

    payload = {
            "model": model_details["model"],
            "messages": messages,
            "stream": stream
        }

    response = requests.post(
        url=url,
        headers=headers,
        data=json.dumps(payload),
        stream=stream
    )

    if response.status_code != 200 and "error" in response.json():
        error = response.json()["error"]

        if error['code'] == 500:
            st.error("The Server is Down. Please try again")
        st.error(f"Error Code: {error['code']} \nError Message: {error['message']}")

        return False

    else:
        if stream is False:
            result = response.json()["choices"][0]["message"]["content"]
            return result

        else:
            return generate_open_router_streaming_response(response)

def generate_open_router_streaming_response(response):
    client = SSEClient(response)

    for event in client.events():
        if event.data == '[DONE]':
            break

        try:
            parsed = json.loads(event.data)
            content = parsed.get("choices", [{}])[0].get("delta", {}).get("content")
            if content:
                yield content
        except json.JSONDecodeError:
            continue

def generate_ollama_response(messages,model_details, stream=False):

    endpoint = "/api/chat"
    url = urljoin(model_details["base_url"], endpoint)

    payload = {
        "model": model_details["model"],
        "messages": messages,
        "stream": stream
    }

    response = requests.post(
        url=url,
        data=json.dumps(payload),
        stream=stream
    )
    if response.status_code != 200:
        if "error" in response.json():
            error = response.json()["error"]
            st.error(f"Error Code: {error['code']} \nError Message: {error['message']}")

    else:
        if stream is False:
            result = response.json()["message"]["content"]
            return result

        else:
            return generate_ollama_streaming_response(response)

def generate_ollama_streaming_response(response):
    try:
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():  # Skip empty lines
                try:
                    json_obj = json.loads(line)

                    # Check if streaming is complete
                    if json_obj.get("done", False):
                        break

                    # Extract content from the message
                    content = json_obj.get("message", {}).get("content", "")
                    if content:  # Only yield non-empty content
                        yield content

                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse JSON line: {line[:100]}...")
                    continue

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return

def render_analysis(analysis):

    md = markdown_it.MarkdownIt(options_update={'breaks':True,'html':True})
    html_text = md.render(analysis)
    st.markdown(f'''
    <div style="font-size: 1.1em;">
    {html_text}</div>
    ''', unsafe_allow_html=True)

@st.cache_data(ttl=600)
def generate_analysis_pdf(analyis):

    buffer = BytesIO()

    analyis_html = markdown_it.MarkdownIt(options_update = {'breaks': True, 'html': True}).render(analyis)
    font_config = FontConfiguration()
    html = HTML(string=f'<html><body>{analyis_html}</body></html>')
    css = CSS(filename=r'./pdf-styling.css',font_config=font_config)
    html.write_pdf(buffer, stylesheets=[css],font_config=font_config)

    return buffer.getvalue()

def analysis_download_button(analysis):

    st.download_button(
        label="Download as PDF",
        data=generate_analysis_pdf(analysis),
        file_name="Resume Analysis.pdf",
        mime="application/pdf",
        icon=":material/download:",
        on_click="ignore",
        type="primary"
    )

def chatbot(model_details):

    if ("chat_messages" not in st.session_state) or st.session_state.chat_messages == []:
        st.session_state.messages.append({"role": "system","content": "Continue acting as a seasoned career coach. Stay engaged in the conversation, answer follow-up questions based on the previous resume analysis, and provide thoughtful, concise, and tailored responses that guide the user toward improving their job application strategy."})

        st.session_state.messages.append({"role":"assistant", "content": "Is there anything you'd like to ask?"})
        st.session_state.chat_messages = [{"role":"assistant", "content": "Is there anything you'd like to ask?"}]

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    prompt = st.chat_input()

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        response_recieved = False
        with st.chat_message("assistant"):
            with st.spinner("Generating..."):
                if model_details["llm_provider"] == "Open Router":
                    if response_generator := generate_open_router_response(st.session_state.messages,model_details, stream=True):
                        response = st.write_stream(response_generator)
                        response_recieved = True

                if model_details["llm_provider"] == "Ollama":
                    if response_generator := generate_ollama_response(st.session_state.messages,model_details, stream=True):
                        response = st.write_stream(response_generator)
                        response_recieved = True

        if response_recieved:
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.chat_messages.append({"role": "assistant", "content": response})

def main():
    load_dotenv()

    st.set_page_config(page_title="AI Resume Critiquer", page_icon="📄", layout="centered")

    if "first_run" not in st.session_state:
        st.session_state.first_run = True

    with st.sidebar:
        setup_model()

    st.title("AI Resume Critiquer")
    st.markdown("🔗 GitHub Link: [AI-Resume-Critiquer](https://github.com/syedmuneeruddin5/AI-Resume-Critiquer.git)")
    st.markdown("Upload your resume and get AI-powered feedback tailored to your needs")

    with st.form("resume_details"):
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'txt'])

        job_description = get_job_description()
        job_industry = job_description["job_industry"]
        job_role = job_description["job_role"]

        analyze = st.form_submit_button("Analyze Resume")


    if "already_analyzed" not in st.session_state:
        st.session_state.already_analyzed = False

    elif "analysis_content" in st.session_state and not analyze:
        render_analysis(st.session_state.analysis_content)
        analysis_download_button(st.session_state.analysis_content)

    if analyze:
        if uploaded_file:
            with st.spinner("Parsing the Resume", show_time=True):

                file_content = extract_text_from_file(uploaded_file)

                if file_content.strip() == "":
                    st.error("Resume does not contain any text")
                    st.stop()

            with st.spinner("Generating Analysis", show_time=True):

                analysis = generate_analysis(file_content, st.session_state.model_details, job_industry, job_role)

            if analysis:

                if "chat_messages" in st.session_state:
                    st.session_state.chat_messages = []

                analysis_content = analysis["response"]
                st.session_state.messages = analysis["messages"]

                st.session_state.already_analyzed = True
                st.session_state.analysis_content = analysis_content

                render_analysis(analysis_content)

                analysis_download_button(analysis_content)

            else:
                st.error("No Analysis Generated")
                st.stop()

        else:
            st.error("No Resume Uploaded")
            st.stop()

    if st.session_state.already_analyzed:
        st.divider()
        chatbot(st.session_state.model_details)

if __name__ == "__main__":
    main()
