"""PDF Report Generator for Interview Feedback"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime
import os
from io import BytesIO

class InterviewReportPDF:
    """Generate professional PDF reports for interview feedback"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=16
        ))
    
    def _draw_header(self, canvas, doc):
        """Draw header on each page"""
        canvas.saveState()
        
        # Header background
        canvas.setFillColor(colors.HexColor('#667eea'))
        canvas.rect(0, letter[1] - 60, letter[0], 60, fill=True, stroke=False)
        
        # Company name
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 20)
        canvas.drawString(50, letter[1] - 35, 'TalentSync')
        
        # Tagline
        canvas.setFont('Helvetica', 10)
        canvas.drawString(50, letter[1] - 50, 'AI-Powered Interview Platform')
        
        # Date
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(letter[0] - 50, letter[1] - 35, 
                              f"Generated: {datetime.now().strftime('%B %d, %Y')}")
        
        canvas.restoreState()
    
    def _draw_footer(self, canvas, doc):
        """Draw footer on each page"""
        canvas.saveState()
        
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#e5e7eb'))
        canvas.setLineWidth(1)
        canvas.line(50, 50, letter[0] - 50, 50)
        
        # Footer text
        canvas.setFillColor(colors.HexColor('#9ca3af'))
        canvas.setFont('Helvetica', 8)
        canvas.drawString(50, 35, '© 2024 TalentSync. All rights reserved.')
        canvas.drawRightString(letter[0] - 50, 35, f'Page {doc.page}')
        
        canvas.restoreState()
    
    def _create_score_chart(self, scores):
        """Create a bar chart for scores"""
        drawing = Drawing(400, 200)
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        chart.data = [scores.values()]
        chart.categoryAxis.categoryNames = list(scores.keys())
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 100
        chart.bars[0].fillColor = colors.HexColor('#667eea')
        
        drawing.add(chart)
        return drawing
    
    def generate_candidate_report(self, candidate_data, feedback_data, output_path=None):
        """Generate PDF report for candidate"""
        if output_path is None:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                   topMargin=80, bottomMargin=70)
        else:
            doc = SimpleDocTemplate(output_path, pagesize=letter,
                                   topMargin=80, bottomMargin=70)
        
        story = []
        
        # Title
        title = Paragraph(f"Interview Feedback Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Candidate Information
        candidate_info = [
            ['Candidate Name:', candidate_data.get('name', 'N/A')],
            ['Email:', candidate_data.get('email', 'N/A')],
            ['Position:', candidate_data.get('job_title', 'N/A')],
            ['Company:', candidate_data.get('company_name', 'N/A')],
            ['Interview Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        info_table = Table(candidate_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Overall Score - Highlighted Box
        overall_score = feedback_data.get('overall_score', 0)
        score_header = Paragraph("Overall Performance Score", self.styles['CustomSubtitle'])
        story.append(score_header)
        
        score_data = [[Paragraph(f"<font size=36 color='#667eea'><b>{overall_score}/100</b></font>", 
                                self.styles['CustomBody'])]]
        score_table = Table(score_data, colWidths=[6*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#f59e0b')),
            ('ROUNDEDCORNERS', [10, 10, 10, 10])
        ]))
        story.append(score_table)
        story.append(Spacer(1, 25))
        
        # Detailed Scores
        scores_header = Paragraph("Detailed Performance Metrics", self.styles['SectionHeader'])
        story.append(scores_header)
        
        scores_data = [
            ['Metric', 'Score', 'Rating'],
            ['Technical Skills', f"{feedback_data.get('technical_score', 0)}/100", 
             self._get_rating(feedback_data.get('technical_score', 0))],
            ['Communication', f"{feedback_data.get('communication_score', 0)}/100",
             self._get_rating(feedback_data.get('communication_score', 0))],
            ['Confidence', f"{feedback_data.get('confidence_score', 0)}/100",
             self._get_rating(feedback_data.get('confidence_score', 0))],
            ['Problem Solving', f"{feedback_data.get('problem_solving_score', 0)}/100",
             self._get_rating(feedback_data.get('problem_solving_score', 0))]
        ]
        
        scores_table = Table(scores_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 25))
        
        # Strengths
        strengths_header = Paragraph("✓ Key Strengths", self.styles['SectionHeader'])
        story.append(strengths_header)
        
        strengths = feedback_data.get('strengths', ['Good participation'])
        for strength in strengths:
            bullet = Paragraph(f"• {strength}", self.styles['CustomBody'])
            story.append(bullet)
        story.append(Spacer(1, 20))
        
        # Areas for Improvement
        improvement_header = Paragraph("→ Areas for Growth", self.styles['SectionHeader'])
        story.append(improvement_header)
        
        weaknesses = feedback_data.get('weaknesses', ['Continue practicing'])
        for weakness in weaknesses:
            bullet = Paragraph(f"• {weakness}", self.styles['CustomBody'])
            story.append(bullet)
        story.append(Spacer(1, 20))
        
        # Detailed Summary
        summary_header = Paragraph("Detailed Assessment", self.styles['SectionHeader'])
        story.append(summary_header)
        
        summary = feedback_data.get('summary', 'No detailed summary available.')
        summary_para = Paragraph(summary, self.styles['CustomBody'])
        story.append(summary_para)
        story.append(Spacer(1, 20))
        
        # Recommendations
        rec_header = Paragraph("Recommendations for Future Interviews", self.styles['SectionHeader'])
        story.append(rec_header)
        
        recommendations = feedback_data.get('recommendations', [
            'Practice regularly',
            'Prepare thoroughly',
            'Stay confident'
        ])
        for rec in recommendations:
            bullet = Paragraph(f"• {rec}", self.styles['CustomBody'])
            story.append(bullet)
        
        # Build PDF
        doc.build(story, onFirstPage=self._draw_header, onLaterPages=self._draw_header)
        
        if output_path is None:
            buffer.seek(0)
            return buffer
        return output_path
    
    def _get_rating(self, score):
        """Convert score to rating"""
        if score >= 90:
            return "Excellent ⭐⭐⭐⭐⭐"
        elif score >= 75:
            return "Very Good ⭐⭐⭐⭐"
        elif score >= 60:
            return "Good ⭐⭐⭐"
        elif score >= 45:
            return "Fair ⭐⭐"
        else:
            return "Needs Improvement ⭐"

def generate_interview_pdf(candidate_data, feedback_data, output_path=None):
    """Convenience function to generate PDF report"""
    generator = InterviewReportPDF()
    return generator.generate_candidate_report(candidate_data, feedback_data, output_path)
