# newsletter_sender.py
# ------------------------------------------------------------
# Simple Email Marketing / Newsletter sender
# Single-file script for small/medium business campaigns
# ------------------------------------------------------------

import csv, os, sys, time, argparse, smtplib, ssl, socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "user@example.com")
SMTP_PASS = os.getenv("SMTP_PASS", "yourpassword")
FROM_NAME = os.getenv("FROM_NAME", "Acme Marketing")
FROM_EMAIL = os.getenv("FROM_EMAIL", "news@acmemarketing.com")

BATCH_SIZE = 50
DELAY_PER_EMAIL = 0.8
DELAY_BETWEEN_BATCH = 5
UNSUBSCRIBE_BASE = "mailto:unsubscribe@yourdomain.com?subject=Unsubscribe"

HTML_TEMPLATE = """
<html><body>
  <h2>Hello {{name}},</h2>
  <p>This month’s newsletter is crafted specially for <b>{{company}}</b>.</p>
  <p><a href="{{cta_link}}">Click here</a> to request a quick audit.</p>
  <p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>
</body></html>
"""

PLAIN_TEMPLATE = """
Hello {{name}},

This month’s newsletter is crafted specially for {{company}}.

Request audit: {{cta_link}}

Unsubscribe: {{unsubscribe_url}}
"""

def load_recipients(csv_path):
    recipients = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get("subscribed","yes").lower() not in ("yes","y","1","true"):
                continue
            recipients.append({
                "email": row.get("email","").strip(),
                "name": row.get("name","there"),
                "company": row.get("company","your company")
            })
    return recipients

def render(template, ctx):
    text = template
    for k,v in ctx.items():
        text = text.replace("{{"+k+"}}", v)
    return text

def create_message(subject, to, html_body, text_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to
    msg.attach(MIMEText(text_body, "plain","utf-8"))
    msg.attach(MIMEText(html_body, "html","utf-8"))
    return msg

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--recipients","-r",required=True)
    p.add_argument("--subject","-s",required=True)
    p.add_argument("--cta",default="https://your-site.example/audit")
    p.add_argument("--test",action="store_true")
    args = p.parse_args()

    recips = load_recipients(args.recipients)
    if not recips: sys.exit("No recipients")

    msgs=[]
    for r in recips:
        unsub=f"{UNSUBSCRIBE_BASE}&email={r['email']}"
        ctx={"name":r["name"],"company":r["company"],"unsubscribe_url":unsub,"cta_link":args.cta}
        html=render(HTML_TEMPLATE,ctx); plain=render(PLAIN_TEMPLATE,ctx)
        msgs.append({"to":r["email"],"msg":create_message(args.subject,r["email"],html,plain)})

    if args.test:
        print("TEST MODE – preview of first message:\n")
        print(msgs[0]["msg"].as_string())
        return

    ctx=ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST,SMTP_PORT,timeout=30) as s:
        s.starttls(context=ctx); s.login(SMTP_USER,SMTP_PASS)
        for i,m in enumerate(msgs,1):
            try:
                s.sendmail(FROM_EMAIL,m["to"],m["msg"].as_string())
                print("Sent to",m["to"])
            except Exception as e: print("ERROR",m["to"],e)
            time.sleep(DELAY_PER_EMAIL)
            if i % BATCH_SIZE==0: time.sleep(DELAY_BETWEEN_BATCH)

if __name__=="__main__": main()
