prompt_career_summary="""
Act as an HR expert and resume writer specializing in ATS-friendly resumes. Your task is to create a professional and polished summary for the resume. 
You are an expert resume writer. Using the applicant's resume information, and the job description, generate an ATS-friendly career summary. Ensure that the summary is clear, attractive, and demonstrates the applicant’s strong fit for the job. Use the following structure:

** Output Template to use **
<div>
    <p align="left" class="career-summary">
       I am a seasoned [Insert the verb/noun combination that describes applicant, for example 'project manager', or 'data science leader']. 
       I [include what you do for the employer, relevant for the job description, for example, 'I build teams and deliver innovative products that disrupt markets'].
       During my career [include one or two most important achievements, directly relevant for the job description]  
    <p><strong>Years of Technical Experience: </strong>[Insert total years of technical experience related to the job and a brief description of the experience aligned with the job description]</p>
    <p><strong>Years of Leadership Experience: </strong>[Insert total years of leadership and management experience related to the job]</p>
    <p><strong>Contributions:</strong>[Highlight key areas where applicant can contribute to the organzation success by considering the job description]</p>
    <p><strong>Core Competencies: </strong>[Mention 3-5 core competencies that match the job requirements]</p>
    <p><strong>Key Achievements: </strong>[Insert 1-3 key achievements that show measurable impact and match job needs]</p>
    <p><strong>Technical/Professional Skills: </strong>[Insert technical or professional skills relevant to the job, matching keywords from the job description]</p>
</div>

- **Job Description:**  
  {job_description}

- **Education Summary:**  
  {education_summary}

- **Experience Details:**
  {experience_details}

- **Minimum Years of Technical Experience:**
    {min_tech_experience}
    
- **Minimum Years of Leadership and Management Experience**
    {min_mgmt_experience}

Instructions:

Use the applicant’s resume for relevant professional experience, achievements, and technical skills.
Use the job description for the job title, required competencies, expectations, and technical skills.
Emphasize noticieable and relevant achievements, measurable results, and specific contributions that highlights the fit to the specified role
Output should be valid HTML code without additional explanations or comments  and also without ```html ```
"""

prompt_header = """
Act as an HR expert and resume writer specializing in ATS-friendly resumes. Your task is to create a professional and polished header for the resume. The header should:

1. **Contact Information**: Include your full name, city and country, phone number, email address, LinkedIn profile, and GitHub profile.
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
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_education = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to articulate the educational background for a resume, ensuring it aligns with the provided job description. For each educational entry, ensure you include:

1. **Institution Name and Location**: Specify the university or educational institution’s name and location.
2. **Degree and Field of Study**: Clearly indicate the degree earned and the field of study.
3. **GPA**: Include your GPA if it is strong and relevant.
4. **Relevant Coursework**: List key courses with their grades to showcase your academic strengths.

Ensure the information is clearly presented and emphasizes academic achievements that align with the job description.

- **My information:**  
  {education_details}

- **Job Description:**  
  {job_description}

- **Template to Use**
```
<section id="education">
    <h2>Education</h2>
    <div class="entry">
      <div class="entry-header">
          <span class="entry-name">[University Name]</span>
          <span class="entry-location">[Location] </span>
      </div>
      <div class="entry-details">
          <span class="entry-title">[Degree] in [Field of Study] | GPA: [Your GPA]/4.0</span>
          <span class="entry-year">[Start Year] – [End Year]  </span>
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
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```"""

prompt_professional_experience = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to detail the work experience for a resume, ensuring it aligns with the provided job description, applicant's position, applicant's skills, and draft experience. 
For each job entry, ensure you include:

"""

prompt_work_experience = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to detail the work experience for a resume, ensuring it aligns with the provided job description. For each job entry, ensure you include:
Ensure that the created work experience builds on top of relevant applicant's experience and aligns well with the job description.
Ensure that the descriptions highlight relevant experience and align with the job description.

You will receive the following inputs:
** Job Description
** Position Title
** List of Applicant Skills
** Experience Details

Analyze these inputs and generate a list of three items based on the draft of work done, ensuring the responses are aligned with the job description and position title. The output should include:

Describe the applicant's responsibilities and achievements in the role.
Highlight any key projects or technologies the applicant worked with that had an impact.
Mention any notable accomplishments or results achieved by the applicant.

- **Job Description:**  
  {job_description}

- **Position Title:**
  {position}

- **List of Applicant Skills:**  
  {skills}
  
- **Experience Details:**
  {experience_details}

- **Output Template to Use**
```
<li class="compact-list">[Describe your responsibilities and achievements in this role]</li>
<li class="compact-list">[Describe any key projects or technologies you worked with that had an impact]</li>
<li class="compact-list">[Mention any notable accomplishments or results]</li>
```

The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```

"""

prompt_side_projects = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to highlight notable side projects based on the provided job description. For each project, ensure you include:

1. **Project Name and Link**: Provide the name of the project and include a link to the GitHub repository or project page.
2. **Project Details**: Describe any notable recognition or achievements related to the project, such as GitHub stars or community feedback.
3. **Technical Contributions**: Highlight your specific contributions and the technologies used in the project.

Ensure that the project descriptions demonstrate your skills and achievements relevant to the job description.

- **My information:**  
  {projects}

- **Job Description:**  
  {job_description}

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
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to list significant achievements based on the provided job description. For each achievement, ensure you include:

1. **Award or Recognition**: Clearly state the name of the award, recognition, scholarship, or honor.
2. **Description**: Provide a brief description of the achievement and its relevance to your career or academic journey.

Ensure that the achievements are clearly presented and effectively highlight your accomplishments.

- **My information:**  
  {achievements}
  {certifications}

- **Job Description:**  
  {job_description}

- **Template to Use**
```
<section id="achievements">
    <h2>Achievements</h2>
    <ul class="compact-list">
      <li><strong>[Award or Recognition or Scholarship or Honor]:</strong> [Describe]
      </li>
      <li><strong>[Award or Recognition or Scholarship or Honor]:</strong> [Describe]
      </li>
      <li><strong>[Award or Recognition or Scholarship or Honor]:</strong> [Describe]
      </li>
    </ul>
</section>
```
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_professional_experience_role_summary = """
Act as an HR expert and experienced resume writer with a specialization in creating ATS-friendly resumes for executives. 
Your task is to summarize the work experience highlighting what specifically this role were expected to do, ensuring it aligns with the provided job description, applicant's experience, applicant's skills, and the job title. 
Ensure that the created work experience summary builds on top of relevant applicant's experience and aligns well with the job description. Be specific and relevant to this position. 
For example, it may say: "In this role I was tasked with building new machine learning platform, leading and growing the team of data science engineers"
It will involve a thorough and deep analysis of job description, aplicant's experience, and customary responsibility of the job title. 
Combine and merge it togheter in a very brief, concise, and a high level, executive like summary. Limit it to one sentence. 
Output just the summary and nothing else. 

**Job Description:**
{job_desc}

**Applicant's Work Experience:**
{work_experience}

**Job Title:**
{position_title}

**Applicant's Skills**
{skills}
"""

prompt_additional_skills = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. 
Your task is to list skills relevant to the job based on the provided job description. For each skill, ensure you include:

1. **Skill Category**: Clearly state the category or type of skill.
2. **Specific Skills**: List the specific skills or technologies within each category.
3. **Proficiency and Experience**: Briefly describe your experience and proficiency level.

Ensure that the skills listed are relevant and accurately reflect your expertise in the field. Remove duplicates. 
At the end, the last section is "Other Skills" - include all other skills that were not included earlier. Group them under the following categories and create a bulleted list: 
- Technical Skills: [list comma separated technical skills only]
- Leadership and Management: [list comma separated leadership and management skills only] 
- Business and Domain knowledge: [list comma separated business and domain knowledge skills only]
- Soft Skill: [list comma separated soft skills only]s
- AI Skills: [list comma separated AI-specific skills only]
- Ethics and Governance: [list comma separated ethics and governance skills only] 

- **My information:**  
  {languages}
  {interests}
  {skills}

- **Job Description:**  
  {job_description}

- **Template to Use**
'''
<section id="skills-languages">
    <h2>Relevant Skills</h2>
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
          <li>Languages: </li>
      </ul>
    </div>
</section>
'''
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

prompt_additional_skills_groupped = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. 
Your task is to list skills relevant to the job based on the provided job description. Analyze each skill and put it under one of the following categories, ensure you include:

1. **Skill Category**: Clearly state the category or type of skill.
2. **Specific Skills**: List the specific skills or technologies within each category.
3. **Proficiency and Experience**: Briefly describe your experience and proficiency level.

Ensure that the skills listed are relevant and accurately reflect your expertise in the field. Remove duplicates. 
At the end, the last section is "Less Relevant Skills" - include all other skills that were not included earlier. Group them under the following categories: 
- Technical Skills
- Leadership and Management
- Business and Domain knowledge
- Soft Skills
- AI Skills
- Ethics and Governance 

- **My information:**  
  {languages}
  {interests}
  {skills}

- **Job Description:**  
  {job_description}

- **Template to Use**
'''
<section id="skills-languages">
    <h2>Additional Relevant Skills</h2>
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
          <li>Languages: </li>
      </ul>
    </div>
</section>
'''
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```
"""

summarize_prompt_template = """
As a seasoned HR expert, your task is to identify and outline the key skills and requirements necessary for the position of this job. Use the provided job description as input to extract all relevant information. This will involve conducting a thorough analysis of the job's responsibilities and the industry standards. You should consider both the technical and soft skills needed to excel in this role. Additionally, specify any educational qualifications, certifications, or experiences that are essential. Your analysis should also reflect on the evolving nature of this role, considering future trends and how they might affect the required competencies.

Rules:
Remove boilerplate text
Include only relevant information to match the job description against the resume

# Analysis Requirements
Your analysis should include the following sections:
Technical Skills: List all the specific technical skills required for the role based on the responsibilities described in the job description.
Soft Skills: Identify the necessary soft skills, such as communication abilities, problem-solving, time management, etc.
Educational Qualifications and Certifications: Specify the essential educational qualifications and certifications for the role.
Professional Experience: Describe the relevant work experiences that are required or preferred.
Role Evolution: Analyze how the role might evolve in the future, considering industry trends and how these might influence the required skills.

# Final Result:
Your analysis should be structured in a clear and organized document with distinct sections for each of the points listed above. Each section should contain:
This comprehensive overview will serve as a guideline for the recruitment process, ensuring the identification of the most qualified candidates.

# Job Description:
```
{text}
```

---

# Job Description Summary"""


prompt_application_title = """
you are an expert job description analyst. Carefully analyze provided job description and create the most relevant position title. Return just the title: 

**Job Description**
{job_description}
"""

prompt_position_hierarchy = """
you are an expert job description analyst. Based on the provided job description determine the most relevant position title. Starting from the most relevant position title as L0, create the reporting hierarchy of steadily increasing responsibility and authority. When creating hierarchy use only one position title for each level 
Output only positions in a comma-delimited string, ordered from L0 to L3, where L0 reports to L1, L1 reports to L2, and L2 reports to L3. L0<L1<L2<L3. Do not output anything else. 

**Job Description**
{job_description}
"""
