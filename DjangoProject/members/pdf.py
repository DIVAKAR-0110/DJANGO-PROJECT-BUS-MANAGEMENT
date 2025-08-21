from fpdf import FPDF

user_details={
    "Name":"Nivash",
    "Email":"rdivakar0110@gmail.com",
    "Phone":"+91 8015165547",
    "Address":"17,R.K.MILLS 'B' Colony,Peelamedu Pudur,Coimbatore"
}

pdf=FPDF()
pdf.add_page()
pdf.set_font("Arial",size=12)

pdf.cell(200,10,txt="User Details Report",ln=True,align='C')
pdf.ln(20)

for key,value in user_details.items():
    pdf.cell(200,10,txt=f"{key}: {value}",ln=True)

pdf.output("R_Divakar.pdf")
print('file created successfully !')