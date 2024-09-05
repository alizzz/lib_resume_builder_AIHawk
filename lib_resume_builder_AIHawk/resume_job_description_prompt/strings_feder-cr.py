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


prompt_working_experience = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to detail the work experience for a resume, ensuring it aligns with the provided job description. For each job entry, ensure you include:

1. **Company Name and Location**: Provide the name of the company and its location.
2. **Job Title**: Clearly state your job title.
3. **Dates of Employment**: Include the start and end dates of your employment.
4. **Responsibilities and Achievements**: Describe your key responsibilities and notable achievements, emphasizing measurable results and specific contributions.

Ensure that the descriptions highlight relevant experience and align with the job description.

- **My information:**  
  {experience_details}

- **Job Description:**  
  {job_description}

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
          <span class="entry-year">[Start Date] – [End Date] </span>
      </div>
      <ul class="compact-list">
          <li>[Describe your responsibilities and achievements in this role] </li>
          <li>[Describe any key projects or technologies you worked with]  </li>
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
          <span class="entry-year">[Start Date] – [End Date] </span>
      </div>
      <ul class="compact-list">
          <li>[Describe your responsibilities and achievements in this role] </li>
          <li>[Describe any key projects or technologies you worked with]  </li>
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
          <span class="entry-year">[Start Date] – [End Date] </span>
      </div>
      <ul class="compact-list">
          <li>[Describe your responsibilities and achievements in this role] </li>
          <li>[Describe any key projects or technologies you worked with]  </li>
          <li>[Mention any notable accomplishments or results]</li>
      </ul>
    </div>
</section>
```
The results should be provided in html format, Provide only the html code for the resume, without any explanations or additional text and also without ```html ```"""


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

prompt_additional_skills = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. Your task is to list additional skills relevant to the job based on the provided job description. For each skill, ensure you include:

1. **Skill Category**: Clearly state the category or type of skill.
2. **Specific Skills**: List the specific skills or technologies within each category.
3. **Proficiency and Experience**: Briefly describe your experience and proficiency level.

Ensure that the skills listed are relevant and accurately reflect your expertise in the field.

- **My information:**  
  {languages}
  {interests}
  {skills}

- **Job Description:**  
  {job_description}

- **Template to Use**
'''
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
          <li><strong>Languages:</strong> </li>
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



{'footer': '',
 'professional_experience': '<table width="720" cellpadding="0" cellspacing="0"> <col width="140"/> <col width="240"/> <col width="100"/> <col width="75"/> <tr> <td align="left"><b><i>HyperC</i></b></td> <td align="left"><b>Manager ML Engineering</b></td> <td align="right">San Francisco Bay, CA</td> <td align="right">2023-Present</td> </tr> </table> <div align="justify" class="prof-exp-details"> <p><i>Leading a globally distributed engineering team</i></p> <p>Managed a global team dedicated to creating a state-of-the-art scalable distributed AI data and networking platform serving both B2B and B2C customers. Ensured full compliance with government regulations, privacy laws, and ethical standards.</p> <ul> <li><p align="justify" style="margin-bottom: 0.04in">Spearheaded the development of strategic direction and provided visionary leadership across various teams and stakeholders. Formulated and executed strategic objectives in alignment with executive goals, promoting a culture of collaboration and mutual support throughout the organization.</p></li> <li><p>Directed and nurtured a top-tier team, focusing on recruitment, motivation, and retention, transforming the team from a few individuals to over 40 in six years. Maintained attrition rates at twice below the industry average and achieved a 97% rate of employee satisfaction. Cultivated a culture of excellence, accountability, and high standards, fostering the development of new leadership within the team.</p></li> <li>Administered a multimillion-dollar budget throughout the lifecycle of pivotal projects, including the development and deployment of a <b>genAI ML platform</b>, an innovative <b>image processing and content extraction framework</b>, a cutting-edge <b>recommender system</b>, a <b>non-linear search engine</b>, and a comprehensive <b>experimentation</b> platform along with several <b>mobile applications</b>. Achieved a 90% reduction in operational costs and enhanced customer satisfaction by leveraging AI edge processing, substantially increasing business value and EBITDA.</li> <li><p>Developed and presented a compelling pitch deck during M&amp;A transactions, showcasing the company\'s leadership in AI technology and driving investor interest.</p></li> </ul></div> <table width="714" cellpadding="7" cellspacing="0"> <col width="113"/> <col width="239"/> <col width="94"/> <col width="68"/> <tr> <td align="left"><b><i>Google</i></b></td> <td align="left"><b>Head of Data Science, CX lab</b></td> <td align="right">Mountain View, CA</td> <td align="right">2021-2023</td> </tr> </table> <div align="justify" class="prof-exp-details"> <ul> <li><p align="left">Collaborated with marketing and product teams to build a clear vision for a data-driven customer segmentation project. Communicated the strategy internally and externally, aligning feedback, performance reviews, and resource allocation with the company\'s broader goals. The successful implementation of the project resulted in a 12.5% improvement in customer targeting accuracy and a 3.6% increase in customer retention.</p></li> <li><p align="left">Championed diversity and inclusion initiatives within the data science team, implementing an inclusive hiring strategy. Modeled inclusive behavior and facilitated respectful discussions to address bias in data analysis, ensuring equitable outcomes in the team\'s projects and discussions.</p></li> <li><p align="left" >Mentored and coached a team of data scientists to enhance their technical proficiency and foster a culture of continuous self-development. Encouraged research initiatives and “stretch” projects to explore innovative data analysis techniques. The team\'s professional growth led to a 40% increase in data-driven insights, driving strategic decision-making across the organization.</p></li></ul></div> <table width="714" cellpadding="7" cellspacing="0"> <col width="113"/> <col width="239"/> <col width="94"/> <col width="68"/> <tr> <td align="left"><b><i>Tensorsoft</i></b></td> <td align="left"><i>Data Science, AIML, Eng</i></td> <td align="left"><b>Co-founder, CTO and Lead Data Science Engineer</b></td> <td align="right">Mountain View, CA</td> <td align="right">2016-2021</td> </tr> </table> <div align="justify" class="prof-exp-details"> <ul> <li>Developed and integrated customer segmentation for search relevancy</li> <li>Developed and maintained a critical software tools for recommendation engine</li> <li>Played an integral role in the development team</li> </ul></div> <table width="714" cellpadding="7" cellspacing="0"> <col width="113"/> <col width="239"/> <col width="94"/> <col width="68"/> <tr> <td align="left"><b><i>Keenetix</i></b></td> <td align="left"><b>Product Manager, Data Science</b></td> <td align="right">Salem, NH</td> <td align="right">2010-2016</td> </tr> <tr> <td align="left"><b><i>Keenetix</i></b></td> <td align="left"><b>Project Dev Manager, Data Science</b></td> <td align="right">Salem, NH</td> <td align="right">2008-2010</td> </tr> <tr> <td align="left"><b><i>Keenetix</i></b></td> <td align="left"><b>Lead Dev Engineer, Data Science</b></td> <td align="right">Salem, NH</td> <td align="right">2005-2008</td> </tr> </table> <div align="justify" class="prof-exp-details"> <ul> <li><p align="left" style="margin-bottom: 0.04in">Built, lead, and motivated a global distributed engineering team of managers, engineers, and data scientists delivering scalable machine learning solutions in multi-spectral remote sensing for regulated industries, government, and NASA with a focus on customer needs.</p></li> <li><p align="left" style="margin-bottom: 0.04in">Created technical solutions based on sound engineering principals to derive actionable insights and to facilitate business decision-making in real time, by merging GIS, multi-spectral imagery, Lidar, and SAR satellite data with health and climate records to create vulnerability scores and risk maps for WHO.</p></li> </ul></div>',
 'academic_appointments': '',
 'education_summary': '<ul class="education-summary> <li><p align="justify"><b>Doctor of Philosophy (PhD)</b> Tufts University, MA</p></li> <li><p align="justify"><b>MBA</b> <i>Summa Cum Laude</i>, Babson College, MA</p></li> <li><p align="justify" class="education-summary"><b>Master of Science (MSc)</b> St.Petersburg, Russia</p></li> </ul>',
 'career_summary': '<b>I am a seasoned AI/ML executive who drives R&amp;D and innovative solutions through visionary leadership, broad technical expertise, and strategic collaboration</b>. Known for loyalty, impactful results, and a supportive, even-tempered approach for the last two dozen years I deliver sustainable growth with adaptability and continuous learning, fostering and nurturing high-performing internationally distributed teams, extensive collaboration, and x-functional alignment. </p> <p align="left" class="career-summary">During my entire career I’ve been translating business requirements into technical definitions, leading advanced R&amp;D projected and converting it to ground breaking products. I am proficient in the Artificial Intelligence, Machine Learning, Database, Software and Networking technology. I have a proven track record in building robust product analytics, data science, and developing cutting-edge ML algorithms such as computer vision, NLP, classification, supervised/unsupervised learning, and anomaly detection to deliver business impact by solving customer problems and growing revenue. I am skilled in data stewardship, business analytics, and building AI as-a-service in the cloud. I have a proven success in delivering impactful, value-adding solutions, overseeing full product development cycles, and meeting critical milestones. I have a deep passion for research, tolerance for ambiguity, and a positive &quot;can do&quot; attitude with a strong business orientation. </p> <p align="left" class="career-summary"> As you can see below my track record includes over <b>25 years of progressive technical and business experience</b> delivering innovative, business-defining products, and <b>18 years of successful team management and engineering leadership</b> specifically focusing on building and nurturing diverse, geographically distributed teams of engineers and scientists. I demonstrated ability to build a common culture based on trust, ownership and accountability. I excel in team building, resource orchestration, and aligning teams with strategic goals to ensure seamless execution, building a great value for customers and increasing revenue.</p>',
 'application_title': 'Head of Data Science, Analytics, ML Engineering',
 'education': '<ul class="education-summary> <li><p align="justify"><b>Doctor of Philosophy (PhD)</b> Tufts University, MA</p></li> <li><p align="justify"><b>MBA</b> <i>Summa Cum Laude</i>, Babson College, MA</p></li> <li><p align="justify" class="education-summary"><b>Master of Science (MSc)</b> St.Petersburg, Russia</p></li> </ul>',
 'career_timeline': '<table width="720" cellpadding="0" cellspacing="0"> <col width="140"/> <col width="140"/> <col width="240"/> <col width="100"/> <col width="75"/> <tr> <td align="left"><b><i>HyperC</i></b></td> <td align="left"><i>AI Strategy and Product, Data Science, ML Engineering</i></td> <td align="left"><b>Manager AIML Engineering</b></td> <td align="right">San Francisco Bay, CA</td> <td align="right">2023-2024</td> </tr> <tr> <td align="left"><b><i>Google</i></b></td> <td align="left"><i>Data Science, Engineering</i></td> <td align="left"><b>Head of Data Science, CX lab</b></td> <td align="right">Mountain View, CA</td> <td align="right">2021-2023</td> </tr> <tr> <td align="left"><b><i>Tensorsoft</i></b></td> <td align="left"><i>Data Science, AIML, Eng</i></td> <td align="left"><b>Co-founder, CTO and Lead Data Science Engineer</b></td> <td align="right">Mountain View, CA</td> <td align="right">2016-2021</td> </tr> <tr> <td align="left"><b><i>Keenetix</i></b></td> <td align="left"><i>Data Science, Analytics</i></td> <td align="left"><b>Product Manager, Data Science</b></td> <td align="right">Salem, NH</td> <td align="right">2010-2016</td> </tr> <tr> <td align="left"><b><i>Keenetix</i></b></td> <td align="left"><i>Data Science, Analytics</i></td> <td align="left"><b>Project Dev Manager, Data Science</b></td> <td align="right">Salem, NH</td> <td align="right">2008-2010</td> </tr> <tr> <td align="left"><b><i>Keenetix</i></b></td> <td align="left"><i>Data Science, Analytics</i></td> <td align="left"><b>Lead Dev Engineer, Data Science</b></td> <td align="right">Salem, NH</td> <td align="right">2005-2008</td> </tr> <tr> <td align="left"><b><i>Digimarc/Polaroid</i></b></td> <td align="left"><i>Image Analysis, Fraud Detection</i></td> <td align="left"><b>Principal Engineer, Data Eng Lead</b></td> <td align="right">Burlington, MA</td> <td align="right">2002-2005</td> </tr> <tr> <td align="left"><b><i>Comverse Technology</i></b></td> <td align="left"><i>DSP, Speech Recognition</i></td> <td align="left"><b>Principal Software Eng</b></td> <td align="right">Wakefield, MA</td> <td align="right">1999-2002</td> </tr> </table>',
 'applicant_name_header': '<span style="font-variant: small-caps"><b>Alexander Liss</b></span> • +1 (646) 867 0808 • hawk@talkdirect.net',
 'skills': '<section id="skills-languages">\n    <h2>Additional Skills</h2>\n    <div class="two-column">\n      <ul class="compact-list">\n          <li>Project Management Software (Monday.com)</li>\n          <li>Microsoft Excel</li>\n          <li>Agile Methodologies</li>\n          <li>Creative Workflow Management</li>\n          <li>Video Production Coordination</li>\n          <li>Budget Management</li>\n      </ul>\n      <ul class="compact-list">\n          <li>Data Analysis</li>\n          <li>Client Communication</li>\n          <li>Team Collaboration</li>\n          <li>Problem-Solving</li>\n          <li>Continuous Improvement</li>\n          <li><strong>Languages:</strong> English (Fluent), Russian (Native)</li>\n      </ul>\n    </div>\n</section>',
 'achievements': '<section id="achievements">\n    <h2>Achievements</h2>\n    <ul class="compact-list">\n      <li><strong>Winner of Multiple Public Data Science Competitions:</strong> Achieved Kaggle Master® designation, Prize Winner, multiple Team and Top 10 awards (top 1% finish in several machine learning competitions with several thousand participants each).\n      </li>\n      <li><strong>Multiple Patents and Peer-Reviewed Publications:</strong> Multiple patents and publications in peer-reviewed indexed scientific journals on topics of stochastic process modeling, forecasting, decision support framework, disease signatures, statistical analysis, and environmental health.\n      </li>\n      <li><strong>Multiple Recognition Awards:</strong> Received multiple Key Contributor Awards, Team Work Appreciation Awards, and Spotlight Awards for outstanding project management and team collaboration.\n      </li>\n      <li><strong>NSF Grant and Award:</strong> Received National Science Foundation Grants and Awards, presented at multiple international scientific conferences, demonstrating expertise in project execution and research.\n      </li>\n    </ul>\n</section>'}
