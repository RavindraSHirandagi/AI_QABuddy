
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def save_plan_to_pdf(plan_data, output):
    """
    Converts a Test Plan dictionary to a PDF file using ReportLab.
    plan_data: dict
    output: file path string OR file-like object (BytesIO)
    """
    doc = SimpleDocTemplate(output, pagesize=letter)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom Styles
    title_style = styles['Title']
    title_style.spaceAfter = 20
    
    heading_style = styles['Heading2']
    heading_style.textColor = colors.HexColor('#2c3e50')
    heading_style.spaceBefore = 15
    heading_style.spaceAfter = 10
    
    body_style = styles['BodyText']
    body_style.spaceAfter = 10
    
    # Title
    plan_title = plan_data.get('plan_title', 'Test Plan')
    story.append(Paragraph(plan_title, title_style))
    story.append(Spacer(1, 12))
    
    # Sections
    sections = plan_data.get('sections', [])
    if not sections:
        story.append(Paragraph("No sections generated.", body_style))
        
    for section in sections:
        # Heading
        heading = section.get('heading', 'Section')
        story.append(Paragraph(heading, heading_style))
        
        # Content
        content = section.get('content', '')
        
        # Simple parsing for bullets
        lines = content.split('\n')
        
        # We process line by line. If we see bullets, we group them?
        # For simplicity in this v1, just treat lines as paragraphs or list items
        
        bullet_items = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            if line.startswith('* ') or line.startswith('- '):
                # It's a bullet
                bullet_items.append(ListItem(Paragraph(line[2:], body_style)))
            elif line.startswith('1. '):
                 # Treat numbered list as bullet for now or paragraph
                 bullet_items.append(ListItem(Paragraph(line, body_style)))
            else:
                # If we have accumulated bullets, dump them
                if bullet_items:
                    story.append(ListFlowable(bullet_items, bulletType='bullet', start='circle'))
                    bullet_items = []
                
                # Regular paragraph
                story.append(Paragraph(line, body_style))
        
        # Dump remaining bullets
        if bullet_items:
            story.append(ListFlowable(bullet_items, bulletType='bullet', start='circle'))
            
        story.append(Spacer(1, 10))
                    
    try:
        doc.build(story)
        return True
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return False
