prompt_header = """
Act as an HR expert and resume writer specializing in ATS-friendly resumes. Your task is to create a professional and polished header for the resume. The header should:

1. **Contact Information**: Include your full name, city and country, phone number, email address, LinkedIn profile, and GitHub profile. Exclude any information that is not provided.
2. **Formatting**: Ensure the contact details are presented clearly and are easy to read.

- **My information:**  
  {personal_information}

- **Template to Use**
```
<header>
  <h1>[Name and Surname]</h1>
  <div class="contact-info"> 
    <p class="fas fa-map-marker-alt">
      <span>[Your City, Your Country]</span>
    </p> 
    <p class="fas fa-phone">
      <span>[Your Prefix Phone number]</span>
    </p> 
    <p class="fas fa-envelope">
      <span>[Your Email]</span>
    </p> 
    <p class="fab fa-linkedin">
      <a href="[Link LinkedIn account]">LinkedIn</a>
    </p> 
    <p class="fab fa-github">
      <a href="[Link GitHub account]">GitHub</a>
    </p> 
  </div>
</header>
```
The results should be provided in html format, include only the provide information and Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_education = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to articulate the educational background for a resume. For each educational entry, ensure you include:

1. **Institution Name and Location**: Specify the university or educational institution’s name and location.
2. **Degree and Field of Study**: Clearly indicate the degree earned and the field of study.
3. **GPA**: Include your GPA if it is strong and relevant.
4. **Relevant Coursework**: List key courses with their grades to showcase your academic strengths.

- **My information:**  
  {education_details}

- **Template to Use**
```
<section id="education">
    <h2>Education</h2>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name">[University Name]</span>
          <span class="entry-location">[Location]</span>
      </div>
      <div class="entry-details">
          <span class="entry-title">[Degree] in [Field of Study] | GPA: [Your GPA]/4.0</span>
          <span class="entry-year">[Start Year] – [End Year]</span>
      </div>
      <ul class="compact-list">
          <li>[Course Name] → GPA: [Grade]/4.0</li>
          <li>[Course Name] → GPA: [Grade]/4.0</li>
          <li>[Course Name] → GPA: [Grade]/4.0</li>
          <li>[Course Name] → GPA: [Grade]/4.0</li>
          <li>[Course Name] → GPA: [Grade]/4.0</li>
      </ul>
    </div>
</section>
```
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_working_experience = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to detail the work experience for a resume. For each job entry, ensure you include:

1. **Company Name and Location**: Provide the name of the company and its location.
2. **Job Title**: Clearly state your job title.
3. **Dates of Employment**: Include the start and end dates of your employment.
4. **Responsibilities and Achievements**: Describe your key responsibilities and notable achievements, emphasizing measurable results and specific contributions.

- **My information:**  
  {experience_details}

- **Template to Use**
```
<section id="work-experience">
    <h2>Work Experience</h2>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name">[Company Name]</span>
          <span class="entry-location"> — [Location]</span>
      </div>
      <div class="entry-details">
          <span class="entry-title">[Your Job Title]</span>
          <span class="entry-year">[Start Date] – [End Date]</span>
      </div>
      <ul class="compact-list">
          <li>[Describe your responsibilities and achievements in this role]</li>
          <li>[Describe any key projects or technologies you worked with]</li>
          <li>[Mention any notable accomplishments or results]</li>
      </ul>
    </div>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name">[Company Name]</span>
          <span class="entry-location"> — [Location]</span>
      </div>
      <div class="entry-details">
          <span class="entry-title">[Your Job Title]</span>
          <span class="entry-year">[Start Date] – [End Date]</span>
      </div>
      <ul class="compact-list">
          <li>[Describe your responsibilities and achievements in this role]</li>
          <li>[Describe any key projects or technologies you worked with]</li>
          <li>[Mention any notable accomplishments or results]</li>
      </ul>
    </div>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name">[Company Name]</span>
          <span class="entry-location"> — [Location]</span>
      </div>
      <div class="entry-details">
          <span class="entry-title">[Your Job Title]</span>
          <span class="entry-year">[Start Date] – [End Date]</span>
      </div>
      <ul class="compact-list">
          <li>[Describe your responsibilities and achievements in this role]</li>
          <li>[Describe any key projects or technologies you worked with]</li>
          <li>[Mention any notable accomplishments or results]</li>
      </ul>
    </div>
</section>
```
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_side_projects = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to highlight notable side projects. For each project, ensure you include:

1. **Project Name and Link**: Provide the name of the project and include a link to the GitHub repository or project page.
2. **Project Details**: Describe any notable recognition or achievements related to the project, such as GitHub stars or community feedback.
3. **Technical Contributions**: Highlight your specific contributions and the technologies used in the project.

- **My information:**  
  {projects}

- **Template to Use**
```
<section id="side-projects">
    <h2>Side Projects</h2>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name"><i class="fab fa-github"></i> <a href="[Github Repo or Link]">[Project Name]</a></span>
      </div>
      <ul class="compact-list">
          <li>[Describe any notable recognition or reception]</li>
          <li>[Describe any notable recognition or reception]</li>
      </ul>
    </div>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name"><i class="fab fa-github"></i> <a href="[Github Repo or Link]">[Project Name]</a></span>
      </div>
      <ul class="compact-list">
          <li>[Describe any notable recognition or reception]</li>
          <li>[Describe any notable recognition or reception]</li>
      </ul>
    </div>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name"><i class="fab fa-github"></i> <a href="[Github Repo or Link]">[Project Name]</a></span>
      </div>
      <ul class="compact-list">
          <li>[Describe any notable recognition or reception]</li>
          <li>[Describe any notable recognition or reception]</li>
      </ul>
    </div>
</section>
```
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_achievements = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to list significant achievements. For each achievement, ensure you include:

1. **Award or Recognition**: Clearly state the name of the award, recognition, scholarship, or honor.
2. **Description**: Provide a brief description of the achievement and its relevance to your career or academic journey.

- **My information:**  
  {achievements}
  {certifications}

- **Template to Use**
```
<section id="achievements">
    <h2>Achievements</h2>
    <ul class="compact-list">
      <li><strong>[Award or Recognition or Scholarship or Honor]:</strong> [Describe]</li>
      <li><strong>[Award or Recognition or Scholarship or Honor]:</strong> [Describe]</li>
      <li><strong>[Award or Recognition or Scholarship or Honor]:</strong> [Describe]</li>
    </ul>
</section>
```
The results should be provided in **html** format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_additional_skills = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to list additional skills relevant to the job. For each skill, ensure you include:

1. **Skill Category**: Clearly state the category or type of skill.
2. **Specific Skills**: List the specific skills or technologies within each category.
3. **Proficiency and Experience**: Briefly describe your experience and proficiency level.

- **My information:**  
  {languages}
  {interests}
  {skills}

- **Template to Use**
```
<section id="skills-languages">
    <h2>Additional Skills</h2>
    <div class="two-column">
      <ul class="compact-list">
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
      </ul>
      <ul class="compact-list">
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li>[Specific Skill or Technology]</li>
          <li><strong>Languages:</strong></li>
      </ul>
    </div>
</section>
```
The results should be provided in html format, 
Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""
prompt_career_summary="""
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. 
Your task is to update the aplicant's career summary below and make it clearly reflecting the job requirements. 
Make it very attractive to the hiring manager, try to cover as many as possible requirements and skills from job description. 
Create two paragraphs. 
The first paragraph should cover primarily technical proficiency. 
The second paragraph should demonstrate business acumen, superior leadership and team managament abilities. 
Make it easily readeable and nicely flowing. 
It should be clear for any readers who is familiar with job requirements that candidate is an exceptional fit for that position.
Highlight the most important parts.  

#career summary
{career_summary}

#job requirements:
{job requirements}

The results should be provided in html format, 
Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

career_highlights_prompt = """
Act as an HR expert and experienced resume writer with a specialization in creating ATS-friendly resumes for executives.
Your task is to create a professional and polished list of highlights for the applicant's resume that is closely aligned with job requirements and demonstrate an excellent fit of the applicant to the job.
Using the applicant's resume information as a base and tune to align with the job description, generate an ATS-friendly career summary.
Respond in a neutral, informative, and professional tone suitable for business or academic contexts. Return just a list of highlights, and nothing else
In angle brackets are inline instructions. Instruction begins with an open bracket "<" and ends with a closing bracket ">" Replace instruction, including brackets, with the text according to the instructions.
Ensure that the highlights are clear, attractive, and demonstrates the applicant’s strong fit for the job. Use the following structure:
***
    Years of Technical Experience: {years_technical_experience}. <Insert a very brief, not more than 20 words, description of the experience aligned with the job description>
    Years of Leadership Experience: {years_leadership_experience} <Insert a very brief leadership and management experience building high-performance distributed teams related to the job>
    Contributions: <Highlight key areas where applicant can contribute to the organzation success by considering the job description>
    Core Competencies: <Mention 3-5 core competencies that match the job requirements>
    Key Achievements: <Insert 1-3 key achievements that show measurable impact and match job needs>
    Technical/Professional Skills: <Insert a brief technical or professional skills relevant to the job, matching keywords from the job description></p>
***

Use the following materials:
**Resume career summary**
{career_summary}


**Resume highlights**
{career_highlights}


**Years of technical experience**
{years_of_technical_experience}


**Years of management and leadership experience**
{years_of_leaderhsip_experience}


**Experience**
{experiences}


**Achievements**
{achievements}


**Skills**
{skills}


**Job Description**
{job_description}
"""

prompt_career_summary_0="""
Act as an HR expert and experienced resume writer with a specialization in creating ATS-friendly resumes for executives.
Your task is to create a professional and polished list of highlights for the applicant's resume that is closely aligned with job requirements and demonstrate an excellent fit of the applicant to the job.
Using the applicant's resume information as a base and tune to align with the job description, generate an ATS-friendly career summary.
Respond in a neutral, informative, and professional tone suitable for business or academic contexts. Return just a list of highlights, and nothing else
In angle brackets are inline instructions. Instruction begins with an open bracket "<" and ends with a closing bracket ">" Replace instruction, including brackets, with the text according to the instructions.
Ensure that the highlights are clear, attractive, and demonstrates the applicant’s strong fit for the job. Use the following structure:
***
    Years of Technical Experience: {years_technical_experience}. <Insert a very brief, not more than 20 words, description of the experience aligned with the job description>
    Years of Leadership Experience: {years_leadership_experience} <Insert a very brief leadership and management experience building high-performance distributed teams related to the job>
    Contributions: <Highlight key areas where applicant can contribute to the organzation success by considering the job description>
    Core Competencies: <Mention 3-5 core competencies that match the job requirements>
    Key Achievements: <Insert 1-3 key achievements that show measurable impact and match job needs>
    Technical/Professional Skills: <Insert a brief technical or professional skills relevant to the job, matching keywords from the job description></p>
***

Use the following materials:
**Resume career summary**
{career_summary}


**Resume highlights**
{career_highlights}


**Years of technical experience**
{years_of_technical_experience}


**Years of management and leadership experience**
{years_of_leaderhsip_experience}


**Experience**
{experiences}


**Achievements**
{achievements}


**Skills**
{skills}


**Job Description**
{job_description}
"""