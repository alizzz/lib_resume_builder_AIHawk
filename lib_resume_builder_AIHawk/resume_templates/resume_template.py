resume_template="""
<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
	<title></title>
	<style type="text/css">$css
	</style>
</head>
<body lang="en-US" text="#000000" link="#0563c1" vlink="#800000" dir="ltr">
<div title="header" align="center" class="header">$applicant_name_header</div>
<h1 class="title">$application_title</h1>
<h2 align="left">Career Summary</h2>
<div title="career_summary" align="left" class="career-summary">$career_summary</div>
<h2 align="left">Career timeline</h2>
<div title="career_timeline" align="left" class="career-timeline">$career_timeline</div>
<h2 align="left">Education and training summary</h2>
<div title="education_summary" align="left" class="education_summary">$education_summary</div>
<div class="page-break"></div>
<h1 class="section-header">Professional Experience</h1>
<div title="professional_experience" class="professional_experience">$professional_experience</div>
<h1 class="section-header">ACADEMIC APPOINTMENTS And TEACHING</h1>
<div title=academic-appointments align="left" class="academic_appointment">$academic_appointments</div>
<h1 class="section-header">ACHIEVEMENTS AND AWARDS</h1>
<div title="section-achivements">$achievements</div>
<h1 class="section-header">Skills and Competencies</h1>
<div title="skills" class="skills>$skills</div>
<div title="footer"><p align="right" style="footer">$footer</div>
</body>
</html>
"""

resume_template_applicant_name_header="""
   <span style="font-variant: small-caps"><b>$name_prefix $first_name $last_name $name_suffix </b></span>• $applicant_phone • $applicant_email
"""

resume_template_job_experience="""
<table width="720" cellpadding="0" cellspacing="0">
		<col width="140"/>
		<col width="240"/>
		<col width="100"/>
		<col width="75"/>
		<tr>
			<td align="left"><b><i>HyperC</i></b></td>
			<td align="left"><b>Manager ML Engineering</b></td>
			<td align="right">San Francisco Bay, CA</td>
			<td align="right">2023-Present</td>
		</tr>
</table>
<div align="justify" class="prof-exp-details">
	<p><i>Leading a globally distributed engineering team</i></p>
	<p>Managed a global team dedicated to creating a state-of-the-art scalable distributed AI data and networking platform serving both B2B and B2C
	customers. Ensured full compliance with government regulations, privacy laws, and ethical standards.</p>
<ul>
	<li><p align="justify" style="margin-bottom: 0.04in">Spearheaded the development of strategic direction and provided visionary leadership across various teams and stakeholders. Formulated and executed strategic objectives in alignment with executive goals, promoting a culture of collaboration and mutual support throughout the organization.</p></li>
	<li><p>Directed and nurtured a top-tier team, focusing on recruitment, motivation, and retention, transforming the team from a few individuals to over 40 in six years. Maintained attrition rates at twice below the industry average and achieved a 97% rate of employee satisfaction. Cultivated a culture of excellence, accountability, and high standards, fostering the development of new leadership within the team.</p></li>
	<li>Administered a multimillion-dollar budget throughout the lifecycle of pivotal projects, including the development and deployment of a <b>genAI ML platform</b>, an innovative <b>image processing and content extraction framework</b>, a cutting-edge <b>recommender system</b>, a <b>non-linear search engine</b>, and a comprehensive <b>experimentation</b> platform along with several <b>mobile applications</b>. Achieved a 90% reduction in operational costs and enhanced customer satisfaction by leveraging AI edge processing, substantially increasing business value and EBITDA.</li>
	<li><p>Developed and presented a compelling pitch deck during M&amp;A transactions, showcasing the company's leadership in AI technology and driving investor interest.</p></li>
</ul></div>
<table width="714" cellpadding="7" cellspacing="0">
	<col width="113"/>
	<col width="239"/>
	<col width="94"/>
	<col width="68"/>
	<tr>
		<td align="left"><b><i>Google</i></b></td>
		<td align="left"><b>Head of Data Science, CX lab</b></td>
		<td align="right">Mountain View, CA</td>
		<td align="right">2021-2023</td>
	</tr>
</table>
<div align="justify" class="prof-exp-details">
<ul>
	<li><p align="left">Collaborated
	with marketing and product teams to build a clear vision for a
	data-driven customer segmentation project. Communicated the strategy
	internally and externally, aligning feedback, performance reviews,
	and resource allocation with the company's broader goals. The
	successful implementation of the project resulted in a 12.5%
	improvement in customer targeting accuracy and a 3.6% increase in
	customer retention.</p></li>
	<li><p align="left">Championed
	diversity and inclusion initiatives within the data science team,
	implementing an inclusive hiring strategy. Modeled inclusive
	behavior and facilitated respectful discussions to address bias in
	data analysis, ensuring equitable outcomes in the team's projects
	and discussions.</p></li>
	<li><p align="left" >Mentored
	and coached a team of data scientists to enhance their technical
	proficiency and foster a culture of continuous self-development.
	Encouraged research initiatives and “stretch” projects to
	explore innovative data analysis techniques. The team's professional
	growth led to a 40% increase in data-driven insights, driving
	strategic decision-making across the organization.</p></li></ul></div>
<table width="714" cellpadding="7" cellspacing="0">
	<col width="113"/>
	<col width="239"/>
	<col width="94"/>
	<col width="68"/>
	<tr>
		<td align="left"><b><i>Tensorsoft</i></b></td>
		<td align="left"><i>Data Science, AIML, Eng</i></td>
		<td align="left"><b>Co-founder, CTO and Lead Data Science Engineer</b></td>
		<td align="right">Mountain View, CA</td>
		<td align="right">2016-2021</td>
	</tr>
</table>
<div align="justify" class="prof-exp-details">
<ul>
	<li>Developed and integrated customer segmentation for search relevancy</li>
	<li>Developed and maintained a critical software tools for recommendation engine</li>
	<li>Played an integral role in the development team</li>
</ul></div>
<table width="714" cellpadding="7" cellspacing="0">
	<col width="113"/>
	<col width="239"/>
	<col width="94"/>
	<col width="68"/>
	<tr>
			<td align="left"><b><i>Keenetix</i></b></td>
			<td align="left"><b>Product Manager, Data Science</b></td>
			<td align="right">Salem, NH</td>
			<td align="right">2010-2016</td>
		</tr>
		<tr>
			<td align="left"><b><i>Keenetix</i></b></td>
			<td align="left"><b>Project Dev Manager, Data Science</b></td>
			<td align="right">Salem, NH</td>
			<td align="right">2008-2010</td>
		</tr>
		<tr>
			<td align="left"><b><i>Keenetix</i></b></td>
			<td align="left"><b>Lead Dev Engineer, Data Science</b></td>
			<td align="right">Salem, NH</td>
			<td align="right">2005-2008</td>
		</tr>
	</table>
<div align="justify" class="prof-exp-details">
	<ul>
	<li><p align="left" style="margin-bottom: 0.04in">Built,
	lead, and motivated a global distributed engineering team of
	managers, engineers, and data scientists delivering scalable machine
	learning solutions in multi-spectral remote sensing for regulated
	industries, government, and NASA with a focus on customer needs.</p></li>
	<li><p align="left" style="margin-bottom: 0.04in">Created
	technical solutions based on sound engineering principals to derive
	actionable insights and to facilitate business decision-making in
	real time, by merging GIS, multi-spectral imagery, Lidar, and SAR
	satellite data with health and climate records to create
	vulnerability scores and risk maps for WHO.</p></li>
	</ul></div>
"""