# Email Marketing Newsletter Script

A single-file **Python 3 script** to send personalized HTML + plain-text newsletters
to a CSV contact list via SMTP.

## Features
- Add contacts in `recipients.csv`
- Personalize with {{name}}, {{company}}
- HTML + text fallback
- Batch + delay to avoid throttling
- Unsubscribe placeholder

## Usage
```bash
# Set environment variables (or edit in script)
export SMTP_HOST=smtp.sendgrid.net
export SMTP_PORT=587
export SMTP_USER=apikey
export SMTP_PASS=xxxxxx
export FROM_NAME="Acme Marketing"
export FROM_EMAIL="news@acmemarketing.com"

# Test mode (prints first email)
python newsletter_sender.py --recipients recipients.csv --subject "October Newsletter" --test

# Real send
python newsletter_sender.py --recipients recipients.csv --subject "October Newsletter"
# email-marketing-newsletter
Simple Python script to send personalized newsletters to a contact list via SMTP.
