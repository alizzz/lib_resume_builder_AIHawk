resume_template="""
<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
	<title></title>
	<style type="text/css">
		@page { size: 8.5in 11in; margin-left: 0.5in; margin-right: 0.4in; margin-top: 0.5in; margin-bottom: 0.1in }
		p { color: #000000; line-height: 115%; text-align: left; orphans: 2; widows: 2; margin-bottom: 0.1in; direction: ltr; background: transparent }
		p.western { font-family: "Calibri", serif; font-size: 11pt; so-language: en-US }
		p.cjk { font-family: "Calibri"; font-size: 11pt; so-language: en-US }
		p.ctl { font-family: "Tahoma"; font-size: 11pt; so-language: ar-SA }
		h1 {font-family: "Garamond", serif; text-transform: uppercase; color: #000000; letter-spacing: 1.5pt; line-height: 100%; text-align: center; page-break-inside: avoid; orphans: 2; widows: 2; margin-top: 0.08in; margin-bottom: 0in; border-top: 1.50pt solid #000000; border-bottom: none; border-left: none; border-right: none; padding-top: 0.01in; padding-bottom: 0in; padding-left: 0in; padding-right: 0in; direction: ltr; background: transparent }
		h1.western { font-family: "Garamond", serif; font-size: 14pt; so-language: en-US; font-weight: bold }
		h1.cjk { font-family: "Calibri"; font-size: 11pt; so-language: en-US; font-weight: bold }
		h1.ctl { font-family: "Tahoma"; font-size: 11pt; so-language: ar-SA }
		h1.title {font-size: 14pt}
		h1.section-header {font-size: 12pt}
		.header {font-family: Garamond, serif; font-size: 16pt; font-variant: normal; font-weight: normal; line-height: 100%; margin-bottom: 0in; border-top: none; border-bottom: 2.00pt double #000000; border-left: none; border-right: none; padding-top: 0in; padding-bottom: 0.01in; padding-left: 0in; padding-right: 0in}
		a:link { color: #0563c1; text-decoration: underline }
		table {font-family: Garamond, serif; font-size: 10pt; font-weight: normal; font-style: normal;
		       border: none; padding: 0in; orphans: 2; widows: 2; margin-left: 0.025in}
	</style>
</head>
<body lang="en-US" text="#000000" link="#0563c1" vlink="#800000" dir="ltr">
<div title="header" align="center" class="header">$applicant_name_header</div>
<h1 class="title">$application_title</h1>
<h2 align="left">Career Summary</h2>
<div title="career_summary" align="left" class="career_summary">$career_summary</div>
<h2 align="left">Career timeline</h2>
<div title="career_timeline" align="left">$career_timeline</div>
<h2 align="left">Education and training summary</h2>
<div title="education_summary" align="left" class="education_summary"</div>
<h1 class="section-header">Professional Experience</h1>
<div title="professional_experience" class="professional_experience">$professional_experience</div>

"""

resume_template_applicant_name_header="""
   <span style="font-variant: small-caps"><b>$name_prefix $first_name $last_name $name_suffix </b></span>• $applicant_phone • $applicant_email
"""

