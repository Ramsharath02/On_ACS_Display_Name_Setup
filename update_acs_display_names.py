import csv
import subprocess
from datetime import datetime

# === Configuration ===
ACS_EMAIL_SERVICE = "acs-mailcow-domain04"
ACS_RESOURCE_GROUP = "acs-mailcow-rg"
INPUT_CSV = "emails.csv"
LOG_CSV = f"acs_displayname_update_log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

logs = []

def update_acs_display_name(domain_name, sender_username, display_name):
    try:
        update_command = [
            "az", "communication", "email", "domain", "sender-username", "update",
            "--domain-name", domain_name,
            "--email-service-name", ACS_EMAIL_SERVICE,
            "--name", sender_username,
            "--resource-group", ACS_RESOURCE_GROUP,
            "--username", sender_username,
            "--display-name", display_name
        ]
        subprocess.run(update_command, check=True, timeout=60)
        return "Success", ""
    except subprocess.CalledProcessError as e:
        return "Failed", str(e)
    except subprocess.TimeoutExpired:
        return "Timeout", "Command timed out."

def main():
    with open(INPUT_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            email = row["Email"].strip()
            username = row["Username"].strip()
            display_name = row["Display Name"].strip()
            domain = row["Domain"].strip()

            status, error = update_acs_display_name(domain, username, display_name)

            print(f"{'✅' if status == 'Success' else '❌'} {email} → {display_name} ({status})")

            logs.append({
                "Email": email,
                "Username": username,
                "Display Name": display_name,
                "Domain": domain,
                "Status": status,
                "Error Message": error
            })

    # Write log to CSV
    with open(LOG_CSV, "w", newline='') as logfile:
        fieldnames = ["Email", "Username", "Display Name", "Domain", "Status", "Error Message"]
        writer = csv.DictWriter(logfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)

    print(f"\n📄 Log saved to: {LOG_CSV}")

if __name__ == "__main__":
    main()
