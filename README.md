# smart_school

This is a project on creating a smart automatic grading platform, capable of receiving free response answers of students to questions and scoring those responses. While that is the main feature of this platform, it also has other traditional functionalities of an online student management platform such as student registration, test setting, result review, etc.

This work is in partial fulfillment of the requirements for the award of B.Eng in Electrical Electronics Engineering to Chukwuma and Okite, students of the Federal University of Technology Owerri.

Cheers!!!

## ABSTRACT
Automatic grading of free response questions presents a significant challenge in
education. This project addresses this challenge by developing an innovative system
that leverages Natural Language Processing (NLP) technologies, specifically
Sentence Transformers, to grade short responses to questions with high accuracy.
The system is designed as a web-based assessment platform capable of evaluating
multiple-choice, fill-in-the-blanks, and short-response questions. The core
innovation lies specifically in the utilization of sentence embeddings and machine
learning to compare the context of student responses with reference answers. This
context-based approach enhances assessment accuracy and reduces the dependency
on predefined keywords. The project's scope encompasses the design and
implementation of a user-friendly assessment platform. The chapter on methodology
outlines the software development life cycle models employed (agile and
prototyping). The integration of FastAPI for backend development and React.js for
frontend design forms the architecture of the platform. Additionally, Hugging Face's
models are harnessed to enable the NLP-powered grading mechanism. The system
achieves a remarkable grading accuracy of 81.7%, demonstrating the potential of
NLP-based technologies in automating complex assessment tasks. Despite the
inherent challenges, such as variations in student responses and model biases, the
system showcases promising results. This project extends the realm of automatic
grading systems by harnessing the power of NLP, ultimately enhancing the
efficiency and scalability of educational assessment processes. The significance of
this research extends beyond education, as the fusion of NLP and machine learning
can find applications in various domains where accurate and context-aware analysis
of free-response text is crucial.

## Technologies Used
1. FastApi
2. LightGBM, Huggingface Transformers
3. Postgres database
4. SqlAlchemy
5. Alembic
6. Heroku (deployment)

## Postgres Database Schema
![image](https://github.com/chimaobi-okite/smart_school/assets/70687495/465b2146-06bd-422b-bbdf-29d48d15afe6)

## Results

Below are sample screens from the actual web app.

|Sample Screens                            | Sample Screens                            |
| ----------------------------------- | ----------------------------------- |
|![1692700011537](https://github.com/chimaobi-okite/smart_school/assets/70687495/a289288d-818c-42ce-b42b-46a66c1b0a56) |![1692700011596](https://github.com/chimaobi-okite/smart_school/assets/70687495/fa646ef2-8274-4c92-b1aa-0a44d022fb02) |

|Sample Screens                            | Sample Screens                            |
| ----------------------------------- | ----------------------------------- |
|![1692700011567](https://github.com/chimaobi-okite/smart_school/assets/70687495/3cc6bcd4-d4cc-4c1d-94e1-c32a29e66f9b) |  ![1692700011552](https://github.com/chimaobi-okite/smart_school/assets/70687495/4b23d05a-6a72-4be6-a383-512ec50061eb) |

### Steps To Reproduce Results
* visit https://futo-academia.vercel.app/
* Login with email - victor@gmail.com and password - 1234
* View Reliability Engineering (ECE510)
* Click on the assessment tab
* Click on view results
* Analyse the marking process
* Repeat the same steps with remi@gmail.com, amara@gmail.com and janet@gmail.com all with the same password in other to gain more insights on the grading process

  **NOTE: This frontend was rushed and lots of details were missed since we had no funds for perfect frontend work**

## Running the FastAPI Project on Your Computer

### Prerequisites:
  * Python > 3.10 installed on your system.
  * PostgreSQL installed and running on your system.

### Steps:
1. **Clone the GitHub Repository:**

    *bash*
    ```
    git clone https://github.com/chimaobi-okite/smart_school.git
    cd smart_school
    ```

2. **Set up a Virtual Environment:**

    *bash*
    ```
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```
3. **Install Dependencies:**

    *bash*
    ```
    pip install -r requirements.txt
    ```
4. **Configure PostgreSQL:**

    Start PostgreSQL and create a new database for your project.
    * Create a .env file in the project root directory
    * Update your project's database connection configuration in a .env file. Check the app.config file for the required configurations

5. **Run Alembic Migrations:**

    Before running the migrations, ensure that alembic.ini has the correct database URI.
    
    *bash*
    ```
    alembic upgrade head
    ```
6. **Start the FastAPI Application:**

    *bash*
    ```
    uvicorn app.main:app --reload
    ```

7. **Access the API:**

    Open your browser and navigate to http://localhost:8000/. 
    You should see the FastAPI default page. 
    You can also access the auto-generated docs by visiting http://localhost:8000/docs.

## Final Notes
Want to read the full paper/project :)..... Drop me a mail @ okitesamuel28@gmail.com or Email Chukwuma @ Chukwuma.c.kingsley@gmail.com
