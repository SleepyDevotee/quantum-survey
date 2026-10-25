#OS TOOL so Python can run Terminal commands (openssl)
import os

#OPTIONAL VPN CHECK: added because I (the author) almost always have NordVPN on
#All probes for this project were run with the VPN OFF, so every probe has to match
#Teammates who don't use a VPN can delete this block or just type y
print("Your connection right now:")
os.system("curl -s https://ipinfo.io/org")
print()

answer = input("\nIs NordVPN OFF? (y/n): ")
if answer != "y":
    print("Turn off NordVPN, then run this again.")
    exit()
    
#READING sites-for-probing.csv one website at a time, skipping the header row
with open('sites-for-probing.csv', 'r') as total_websites:
    next(total_websites)
    for cells in total_websites:

        #UNPACKING each line into domain, sector, and Tranco rank
        cell_a, cell_b, cell_c = cells.strip().split(",")

        #PROGRESS so you can see which website is being probed
        print("\nDomain:", cell_a)

        #COMMAND for one TLS handshake: offers hybrid first like a modern browser, hides errors, and saves the output to that website's own file
        command = f"echo | openssl s_client -connect {cell_a}:443 -servername {cell_a} -groups X25519MLKEM768:X25519:secp256r1:MLKEM768 2>/dev/null > probe-results/{cell_a}.txt"

        #RUN the command, the same as typing it in Terminal
        os.system(command)