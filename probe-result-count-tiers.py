#TUPLES to prevent accidental mishandlings
sectors = ('Banking', 'Education', 'Government', 'Healthcare', 'News', 'Retail', 'Technology')

#COUNTERS to keep track of the websites scanned and that are considered safe, and totaling every site's score
for sector in sectors:
    count = 0
    safe = 0
    total_score = 0

    #READING tiers.csv one line at a time, skipping the header row
    with open('scores/tiers-2026-10-28.csv') as tiers:
        next(tiers)
        for lines in tiers:

            #SECTOR CHECK to only count the websites that belong to the current sector
            if sector in lines:
                count = count + 1

                #SCORE pulled from the 4th column, turned from text into a number, then added to the total
                total_score = total_score + float(lines.strip().split(",")[3])

                #SAFE CHECK to count the websites using hybrid post-quantum key exchange (Tier 2)
                if 'Tier 2' in lines:
                    safe = safe + 1

    #PERCENTAGES for the share of safe websites and the average risk, skipped if a sector has no websites to avoid dividing by zero
    if count > 0:
        percent = (safe / count) * 100
        average = total_score / count
    else:
        percent = 0
        average = 0

    #READINESS from the roadmap: 100 minus the average risk, so higher means more prepared
    readiness = 100 - average

    #RESULTS printed per sector, rounded to 1 decimal
    print('\n' + sector.upper() + ':', count, 'websites',
          '\nSafe:', safe,
          '\nSecurity Percentage:', round(percent, 1),
          '\nAverage Risk:', round(average, 1),
          '\nReadiness:', round(readiness, 1))