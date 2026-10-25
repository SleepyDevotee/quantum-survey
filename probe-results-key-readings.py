#DATE TOOL for counting the days until a certificate expires
from datetime import date

#MONTHS list so a month name like 'Nov' can be turned into its number (11)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

#HEADER row for tiers.csv, printed once before the loop
print("DOMAIN,SECTOR,TIER,SCORE")

#READING sites-for-probing.csv one website at a time, skipping the header row
with open('sites-for-probing.csv', 'r') as total_websites:
    next(total_websites)
    for cells in total_websites:

        #UNPACKING each line into domain, sector, and Tranco rank
        cell_a, cell_b, cell_c = cells.strip().split(",")

        #DEFAULTS for every website: no connection and 0 points on every layer until the file proves otherwise
        tier = "No connection"
        l1 = 0
        l2a = 0
        l2b = 0
        l2c = 0
        l3 = 0
        expiry = ""
        protocol = ""
        cipher = ""

        #PROBE FILE for this website, read one line at a time
        with open(f'probe-results/{cell_a}.txt', 'r') as key_readings:
            for line in key_readings:

                #L1 TLS VERSION: TLS 1.2 is older and gets 4.5 points, the line is also saved for the RSA check
                if "Protocol" in line:
                    protocol = line
                    if "TLSv1.2" in line:
                        l1 = 4.5

                #L2b CIPHER: AES-128 is weakened by Grover's algorithm and gets 2 points, the line is also saved for the RSA check
                if "Cipher is" in line:
                    cipher = line
                    if "AES_128" in line or "AES128" in line:
                        l2b = 2

                #L3 CERTIFICATE: grabs the expiry date from the first certificate only, since that one belongs to the website
                if "NotAfter:" in line and expiry == "":
                    expiry = line.split("NotAfter: ")[1].strip()

                #L2a KEY EXCHANGE + TIER: decides the tier from the lock the website picked
                if "Negotiated TLS1.3 group" in line or "Peer Temp Key" in line:

                    #HYBRID (MLKEM): quantum-safe, but the classical half still counts 3 points on L1
                    if "MLKEM" in line:
                        tier = "Tier 2 (safe)"
                        l1 = 3
                        l2a = 0

                        #L2c WEAK PQC: ML-KEM-512 is NIST Level 1 and gets 6 points
                        if "MLKEM512" in line:
                            l2c = 6

                    #UNCLEAR: OpenSSL couldn't name the lock, so the website is left out
                    elif "NID: 0" in line:
                        tier = "Unclear"

                    #CLASSICAL (X25519, prime256v1): breakable by a future quantum computer, gets 12 points
                    else:
                        tier = "Tier 1b (not safe)"
                        l2a = 12

        #RSA CHECK: RSA key exchange has no "Peer Temp Key" line, so TLS 1.2 with a working cipher and no DHE means RSA (worst tier)
        if tier == "No connection" and "TLSv1.2" in protocol and "DHE" not in cipher and "NONE" not in cipher and cipher != "":
            tier = "Tier 1a (worst)"
            l1 = 6
            l2a = 20

        #L3 DATE MATH: splits the date into a list, turns each piece into a number, then counts the days left
        if expiry != "":
            parts = expiry.split()
            month = months.index(parts[0]) + 1
            day = int(parts[1])
            year = int(parts[3])

            expiry_date = date(year, month, day)
            days = (expiry_date - date.today()).days

            #EXPIRY POINTS: 5 if already expired, more points the closer it is under 30 days, 0 otherwise
            if days < 0:
                l3 = 5
            elif days < 30:
                l3 = 5 * (30 - days) / 30

        #SCORE from the risk paper: add all 5 layers, times 1.5 (HNDL boost), divided by 118, times 100
        #SKIPPED if the website had no HTTPS connection or an unclear lock, so it doesn't change the averages
        if tier != "No connection" and tier != "Unclear":
            score = round((((l1 + l2a + l2b + l2c + l3) * 1.5) / 118) * 100, 1)
            print(f"{cell_a},{cell_b},{tier},{score}")