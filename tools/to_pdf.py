import sys, os
import win32com.client
import fitz

src = os.path.abspath(sys.argv[1])
pdf = os.path.splitext(src)[0] + '.pdf'
ext = os.path.splitext(src)[1].lower()
if ext == '.docx':
    app = win32com.client.DispatchEx('Word.Application')
    app.Visible = False
    d = app.Documents.Open(src, ReadOnly=True)
    d.SaveAs(pdf, FileFormat=17)
    d.Close(False)
    app.Quit()
else:
    app = win32com.client.DispatchEx('PowerPoint.Application')
    p = app.Presentations.Open(src, WithWindow=False)
    p.SaveAs(pdf, 32)
    p.Close()
    app.Quit()
print('pdf', pdf)

if len(sys.argv) > 2:
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith('.png'): os.remove(os.path.join(out, f))
    doc = fitz.open(pdf)
    for i, page in enumerate(doc):
        page.get_pixmap(dpi=int(sys.argv[3]) if len(sys.argv) > 3 else 70).save(os.path.join(out, f'p{i+1:02d}.png'))
    print('pages', len(doc))
