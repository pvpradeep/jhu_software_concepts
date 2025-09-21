import os
import psycopg
import psycopg_pool


def print_records(records, x = 3, header = None): # pragma: no cover
  print("" + "="*40)
  print(f"Printing {header} ")
  print("" + "="*40)
  if (len(records) < x):
    x = len(records)

  for i, record in enumerate(records, start=1):
    print(f"Record {i}: {record}")
    if i == x:
      break
    if (len(records) > x):
      print(f"... and {len(records) - x} more records")
  print("" + "="*40)

def print_load_summary(pool):
  with pool.connection() as conn:
    with conn.cursor() as cur:
      cur.execute('SELECT COUNT(*) FROM gradrecords')
      total_records = cur.fetchone()[0]
      print(f"Total records in gradrecords table: {total_records}")

      cur.execute('SELECT * FROM gradrecords_latest')
      latest_records = cur.fetchall()
      print(f"Total records in gradrecords_latest table: {len(latest_records)}")
      print_records(latest_records, 5, header="records in gradrecords_latest")

      cur.execute('SELECT * FROM gradrecords LIMIT 5')
      sample_records = cur.fetchall()
      #print_records(sample_records, 5, header="Sample records from gradrecords")

def getQ1(cur):
    cur.execute("SELECT COUNT(*) FROM gradrecords WHERE term = 'Fall 2025'")
    count = cur.fetchone()[0]
    return f"Number of entries in Fall 2025: {count}"

def getQ2(cur):
    cur.execute("SELECT COUNT(*) FROM gradrecords WHERE us_or_international NOT IN ('American')")
    international_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM gradrecords WHERE us_or_international IS NOT NULL")
    total_count = cur.fetchone()[0]
    percentage = (international_count / total_count * 100) if total_count > 0 else 0
    percentage = round(percentage, 2) if percentage is not None else 0.0
    return f"Percentage of international students: {percentage:.2f}%"

def getQ3(cur):
    cur.execute(f"SELECT AVG(gpa) FROM gradrecords WHERE gpa != 0")
    gpa_avg = cur.fetchone()[0]
    gpa_avg = round(gpa_avg, 2) if gpa_avg is not None else 0.0
    cur.execute(f"SELECT AVG(gre) FROM gradrecords WHERE gre != 0")
    gre_avg = cur.fetchone()[0]
    gre_avg = round(gre_avg, 2) if gre_avg is not None else 0.0
    cur.execute(f"SELECT AVG(gre_v) FROM gradrecords WHERE gre_v != 0")
    gre_v_avg = cur.fetchone()[0]
    gre_v_avg = round(gre_v_avg, 2) if gre_v_avg is not None else 0.0
    cur.execute(f"SELECT AVG(gre_aw) FROM gradrecords WHERE gre_aw != 0")
    gre_aw_avg = cur.fetchone()[0]
    gre_aw_avg = round(gre_aw_avg, 2) if gre_aw_avg is not None else 0.0

    return (f"Average GPA: {gpa_avg:>6.2f}    "
            f"     Average GRE: {gre_avg:>6.2f}    "
            f"     Average GRE V: {gre_v_avg:>6.2f}    "
            f"     Average GRE AW: {gre_aw_avg:>6.2f}")
    
def getQ4(cur):
    cur.execute("""
      SELECT AVG(gpa) 
      FROM gradrecords 
      WHERE us_or_international = 'American' AND term = 'Fall 2025' AND gpa != 0
    """)
    avg_gpa_american_fall_2025 = cur.fetchone()[0]
    avg_gpa_american_fall_2025 = round(avg_gpa_american_fall_2025, 2) if avg_gpa_american_fall_2025 is not None else 0.0
    return f"Average GPA of American students in Fall 2025: {avg_gpa_american_fall_2025:.2f}"

def getQ5(cur):
    cur.execute("SELECT COUNT(*) FROM gradrecords WHERE term = 'Fall 2025'")
    fall_2025_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM gradrecords WHERE term = 'Fall 2025' AND status ILIKE '%accepted%'")
    accepted_fall_2025_count = cur.fetchone()[0]
    acceptance_percentage_fall_2025 = (accepted_fall_2025_count / fall_2025_count * 100) if fall_2025_count > 0 else 0
    acp = round(acceptance_percentage_fall_2025, 2) if acceptance_percentage_fall_2025 is not None else 0.0
    return f"Percentage of Acceptances for Fall 2025: {acp:.2f}%"

def getQ6(cur):
    cur.execute("""
      SELECT AVG(gpa) 
      FROM gradrecords 
      WHERE term = 'Fall 2025' AND status ILIKE '%accepted%' AND gpa != 0
    """)
    avg_gpa_accepted_fall_2025 = cur.fetchone()[0]
    avg = round(avg_gpa_accepted_fall_2025, 2) if avg_gpa_accepted_fall_2025 is not None else 0.0
    return f"Average GPA of Acceptances for Fall 2025: {avg:.2f}"

def getQ7(cur):
    cur.execute("""
      SELECT COUNT(*) 
      FROM gradrecords 
      WHERE program ILIKE '%computer science%' AND degree ILIKE '%master%'
    """)
    jhu_cs_masters_count = cur.fetchone()[0]
    csm = round(jhu_cs_masters_count, 2) if jhu_cs_masters_count is not None else 0.0
    return f"Total entries for JHU(to-do) Computer Science Masters: {csm}"

def getQ8(cur):
    cur.execute("""
      SELECT COUNT(*) 
      FROM gradrecords 
      WHERE term = 'Fall 2025' AND status ILIKE '%accepted%' 
        AND llm_generated_university ILIKE '%georgetown%' 
        AND llm_generated_program ILIKE '%computer science%' 
        AND degree ILIKE '%phd%'
    """)
    georgetown_cs_phd_accepted_2025_count = cur.fetchone()[0]
    return f"Ans: Total acceptances for Georgetown Computer Science PhD in Fall 2025: {georgetown_cs_phd_accepted_2025_count}"

def getQ9(cur):
    max_gpa = 4.0
    max_gre = 340
    max_gre_v = 170
    max_gre_aw = 6.0

    cur.execute(f"SELECT AVG(gpa) FROM gradrecords WHERE gpa !=0 AND gpa <= {max_gpa}")
    avg_gpa = cur.fetchone()[0]

    cur.execute(f"SELECT AVG(gre) FROM gradrecords WHERE gre != 0 AND gre <= {max_gre}")
    avg_gre = cur.fetchone()[0]

    cur.execute(f"SELECT AVG(gre_v) FROM gradrecords WHERE gre_v !=0 AND gre_v <= {max_gre_v}")
    avg_gre_v = cur.fetchone()[0]

    cur.execute(f"SELECT AVG(gre_aw) FROM gradrecords WHERE gre_aw !=0 AND gre_aw <= {max_gre_aw}")
    avg_gre_aw = cur.fetchone()[0]
    avg_gpa = round(avg_gpa, 2) if avg_gpa is not None else 0.0
    avg_gre = round(avg_gre, 2) if avg_gre is not None else 0.0
    avg_gre_v = round(avg_gre_v, 2) if avg_gre_v is not None else 0.0
    avg_gre_aw = round(avg_gre_aw, 2) if avg_gre_aw is not None else 0.0

    return (f"Average GPA (no outliers): {avg_gpa:>6.2f},"
            f"     Average GRE (no outliers): {avg_gre:>6.2f},"
            f"     Average GRE V (no outliers): {avg_gre_v:>6.2f},"
            f"     Average GRE AW (no outliers): {avg_gre_aw:>6.2f}")

def getQ10(cur):
    max_gpa = 4.0
    max_gre = 340
    max_gre_v = 170
    max_gre_aw = 6.0

    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gpa !=0 AND gpa > {max_gpa}")
    gpa_outliers = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gpa !=0")
    gpa_valid_count = cur.fetchone()[0]
    gpa_outl_percentage = (gpa_outliers / gpa_valid_count * 100) if gpa_valid_count > 0 else 0

    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre != 0 AND gre > {max_gre}")
    gre_outliers = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre != 0")
    gre_valid_count = cur.fetchone()[0]
    gre_outl_percentage = (gre_outliers / gre_valid_count * 100) if gre_valid_count > 0 else 0

    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_v != 0 AND gre_v > {max_gre_v}")
    grev_outliers = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_v != 0")
    gre_v_valid_count = cur.fetchone()[0]
    grev_outl_percentage = (grev_outliers / gre_v_valid_count * 100) if gre_v_valid_count > 0 else 0

    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_aw != 0 AND gre_aw > {max_gre_aw}")
    greaw_outliers = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_aw != 0")
    gre_aw_valid_count = cur.fetchone()[0]
    greaw_outl_percentage = (greaw_outliers / gre_aw_valid_count * 100) if gre_aw_valid_count > 0 else 0

    gpa_outl_percentage = round(gpa_outl_percentage, 2) if gpa_outl_percentage is not None else 0.0
    gre_outl_percentage = round(gre_outl_percentage, 2) if gre_outl_percentage is not None else 0.0
    grev_outl_percentage = round(grev_outl_percentage, 2) if grev_outl_percentage is not None else 0.0
    greaw_outl_percentage = round(greaw_outl_percentage, 2) if greaw_outl_percentage is not None else 0.0

    return (f"\nGPA outliers: {gpa_outliers}, Percentage of GPA outliers: {gpa_outl_percentage:>6.2f}%\n"
            f"GRE outliers: {gre_outliers}, Percentage of GRE outliers: {gre_outl_percentage:>6.2f}%\n"
            f"GRE V outliers: {grev_outliers}, Percentage of GRE V outliers: {grev_outl_percentage:>6.2f}%\n"
            f"GRE AW outliers: {greaw_outliers}, Percentage of GRE AW outliers: {greaw_outl_percentage:>6.2f}%")

def get_db_summary(pool):
    """
    Generate a comprehensive summary of graduate admissions data from the database.
    
    This function executes a series of analytical queries on the grad records database
    to generate insights about:
    - Fall 2025 application statistics
    - International vs domestic student ratios
    - GPA and GRE score distributions
    - Acceptance rates
    - Program-specific statistics
    - Data quality metrics (outliers)
    
    :param pool: Database connection pool to use for queries
    :type pool: psycopg_pool.ConnectionPool
    :return: List of tuples containing query descriptions and their results
    :rtype: list[tuple[str, str]]
    
    The function aggregates results from multiple query functions:
    - Q1: Fall 2025 entry count
    - Q2: International student percentage
    - Q3: Average test scores
    - Q4: American students' GPA
    - Q5: Fall 2025 acceptance rate
    - Q6: Accepted students' GPA
    - Q7: JHU CS Masters statistics
    - Q8: Georgetown CS PhD statistics
    - Q9: Metrics excluding outliers
    - Q10: Outlier analysis
    """
    queries_and_functions = [
        ("How many entries do you have in your database who have applied for Fall 2025?",getQ1),
        ("What percentage of entries are from interna5onal students (not American or Other) (to two decimal places)?",getQ2),
        ("What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?",getQ3),
        ("What is the average GPA of American students in Fall 2025?",getQ4),
        ("What percent of entries for Fall 2025 are Acceptances (to two decimal places)?",getQ5),
        ("What is the average GPA of applicants who applied for Fall 2025 who are Acceptanced?",getQ6),
        ("How many entries are from applicants who applied to JHU for a masters degrees in Computer Science?",getQ7),
        ("How many entries from 2025 are acceptances from applicants who applied to Georgetown University for a PhD in Computer Science?",getQ8),
        ("Calculate averages excluding outliers",getQ9),
        ("Find number of outliers and % of outliers",getQ10)
    ]
    results = []
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for description, func in queries_and_functions:
                result = func(cur)
                results.append((description, result))
    return results

### Helper / Print functions for debugging

## retain this function for now - to check on terminal
def print_query_results(pool):  # pragma: no cover
  with pool.connection() as conn:
    with conn.cursor() as cur:
      print("\n" + "="*60)
      print("Database Summary and Analysis")
      print("="*60)
      # 1. How many entries do you have in your database who have applied for Fall 2025?
      cur.execute("SELECT COUNT(*) FROM gradrecords WHERE term = 'Fall 2025'")
      fall_2025_count = cur.fetchone()[0]
      print(f"1. Total entries for Fall 2025: {fall_2025_count}")

      # 2. What percentage of entries are from international students (not American or Other) (to two decimal places)?
      cur.execute("SELECT COUNT(*) FROM gradrecords WHERE us_or_international NOT IN ('American')")
      international_count = cur.fetchone()[0]
      cur.execute("SELECT COUNT(*) FROM gradrecords")
      total_count = cur.fetchone()[0]
      international_percentage = (international_count / total_count * 100) if total_count > 0 else 0
      print(f"2. Percentage of international students: {international_percentage:.2f}%")

      # 3. What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?
      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gpa != 0")
      gpa_valid_count = cur.fetchone()[0]
      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre != 0")
      gre_valid_count = cur.fetchone()[0]
      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_v != 0")
      gre_v_valid_count = cur.fetchone()[0]
      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_aw != 0")
      gre_aw_valid_count = cur.fetchone()[0]

      cur.execute(f"SELECT AVG(gpa) FROM gradrecords WHERE gpa != 0")
      gpa_avg = cur.fetchone()[0]
      gpa_avg = round(gpa_avg, 2) if gpa_avg is not None else 0.0
      cur.execute(f"SELECT AVG(gre) FROM gradrecords WHERE gre != 0")
      gre_avg = cur.fetchone()[0]
      gre_avg = round(gre_avg, 2) if gre_avg is not None else 0.0
      cur.execute(f"SELECT AVG(gre_v) FROM gradrecords WHERE gre_v != 0")
      gre_v_avg = cur.fetchone()[0]
      gre_v_avg = round(gre_v_avg, 2) if gre_v_avg is not None else 0.0
      cur.execute(f"SELECT AVG(gre_aw) FROM gradrecords WHERE gre_aw != 0")
      gre_aw_avg = cur.fetchone()[0]
      gre_aw_avg = round(gre_aw_avg, 2) if gre_aw_avg is not None else 0.0

      print(f"3. Average GPA: {gpa_avg:.2f}, Average GRE: {gre_avg:.2f}, Average GRE V: {gre_v_avg:.2f}, Average GRE AW: {gre_aw_avg:.2f}")

      # 4. What is their average GPA of American students in Fall 2025?
      cur.execute("""
        SELECT AVG(gpa) 
        FROM gradrecords 
        WHERE us_or_international = 'American' AND term = 'Fall 2025' AND gpa != 0
      """)
      avg_gpa_american_fall_2025 = cur.fetchone()[0]
      print(f"4. Average GPA of American students in Fall 2025: {avg_gpa_american_fall_2025:.2f}")

      # 5. What percent of entries for Fall 2025 are Acceptances (to two decimal places)?
      cur.execute("SELECT COUNT(*) FROM gradrecords WHERE term = 'Fall 2025' AND status ILIKE '%accepted%'")
      accepted_fall_2025_count = cur.fetchone()[0]
      acceptance_percentage_fall_2025 = (accepted_fall_2025_count / fall_2025_count * 100) if fall_2025_count > 0 else 0
      print(f"5. Percentage of Acceptances for Fall 2025: {acceptance_percentage_fall_2025:.2f}%")

      #6. What is the average GPA of applicants who applied for Fall 2025 who are Acceptances?
      cur.execute("""
        SELECT AVG(gpa) 
        FROM gradrecords 
        WHERE term = 'Fall 2025' AND status ILIKE '%accepted%' AND gpa != 0
      """)
      avg_gpa_accepted_fall_2025 = cur.fetchone()[0]
      print(f"6. Average GPA of Acceptances for Fall 2025: {avg_gpa_accepted_fall_2025:.2f}")

      #7. How many entries are from applicants who applied to JHU for a masters degrees in Computer Science?
      cur.execute("""
        SELECT COUNT(*) 
        FROM gradrecords 
        WHERE llm_generated_program ILIKE '%computer science%' AND degree ILIKE '%master%'
      """)
      jhu_cs_masters_count = cur.fetchone()[0]
      print(f"7. Total entries for JHU Computer Science Masters: {jhu_cs_masters_count}")

      #8. How many entries from 2025 are acceptances from applicants who applied to Georgetown
      #   University for a PhD in Computer Science?
      cur.execute("""
        SELECT COUNT(*) 
        FROM gradrecords 
        WHERE term = 'Fall 2025' AND status ILIKE '%accepted%' 
          AND llm_generated_university ILIKE '%georgetown%' 
          AND llm_generated_program ILIKE '%computer science%' 
          AND degree ILIKE '%phd%'
      """)
      georgetown_cs_phd_accepted_2025_count = cur.fetchone()[0]
      print(f"8. Total acceptances for Georgetown Computer Science PhD in Fall 2025: {georgetown_cs_phd_accepted_2025_count}")

      #9. find outliers and calculate averages excluding outliers
      max_gpa = 4.0
      max_gre = 340
      max_gre_v = 170
      max_gre_aw = 6.0
      # this might mess up averages since some records can have missing values
      '''
      cur.execute(f"""
        SELECT 
          AVG(gpa) AS avg_gpa_no_outliers,
          AVG(gre) AS avg_gre_no_outliers,
          AVG(gre_v) AS avg_gre_v_no_outliers,
          AVG(gre_aw) AS avg_gre_aw_no_outliers
        FROM gradrecords
        WHERE (gpa IS NOT NULL AND gpa <= {max_gpa})
          OR (gre IS NOT NULL AND gre <= {max_gre})
          OR (gre_v IS NOT NULL AND gre_v <= {max_gre_v})
          OR (gre_aw IS NOT NULL AND gre_aw <= {max_gre_aw})
      """)
      avg_metrics_no_outliers = cur.fetchone()
      print(f"9. Average GPA (no outliers): {avg_metrics_no_outliers[0]:.2f},"
            " Average GRE (no outliers): {avg_metrics_no_outliers[1]:.2f},"
            " Average GRE V (no outliers): {avg_metrics_no_outliers[2]:.2f},"
            " Average GRE AW (no outliers): {avg_metrics_no_outliers[3]:.2f}")
      
      '''
      cur.execute(f"SELECT AVG(gpa) FROM gradrecords WHERE gpa !=0 AND gpa <= {max_gpa}")
      avg_gpa = cur.fetchone()[0]

      cur.execute(f"SELECT AVG(gre) FROM gradrecords WHERE gre != 0 AND gre <= {max_gre}")
      avg_gre = cur.fetchone()[0]

      cur.execute(f"SELECT AVG(gre_v) FROM gradrecords WHERE gre_v !=0 AND gre_v <= {max_gre_v}")
      avg_gre_v = cur.fetchone()[0]

      cur.execute(f"SELECT AVG(gre_aw) FROM gradrecords WHERE gre_aw !=0 AND gre_aw <= {max_gre_aw}")
      avg_gre_aw = cur.fetchone()[0]
      print(f"9. Average GPA (no outliers): {avg_gpa:.2f},"
            f" Average GRE (no outliers): {avg_gre:.2f},"
            f" Average GRE V (no outliers): {avg_gre_v:.2f},"
            f" Average GRE AW (no outliers): {avg_gre_aw:.2f}")

      #10. show number of outliers and % of outliers
      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gpa !=0 AND gpa > {max_gpa}")
      gpa_outliers = cur.fetchone()[0]
      
      gpa_outl_percentage = (gpa_outliers / gpa_valid_count * 100) if gpa_valid_count > 0 else 0
      print(f"10. GPA outliers: {gpa_outliers}, Percentage of GPA outliers: {gpa_outl_percentage:.2f}%")

      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre != 0 AND gre > {max_gre}")
      gre_outliers = cur.fetchone()[0]
      outl_percentage = (gre_outliers / gre_valid_count * 100) if gre_valid_count > 0 else 0
      print(f"    GRE outliers: {gre_outliers}, Percentage of GPA outliers: {outl_percentage:.2f}%")

      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_v != 0 AND gre_v > {max_gre_v}")
      grev_outliers = cur.fetchone()[0]
      outl_percentage = (grev_outliers / gre_v_valid_count * 100) if gre_v_valid_count > 0 else 0
      print(f"    GRE V outliers: {grev_outliers}, Percentage of GPA outliers: {outl_percentage:.2f}%")

      cur.execute(f"SELECT COUNT(*) FROM gradrecords WHERE gre_aw != 0 AND gre_aw > {max_gre_aw}")
      greaw_outliers = cur.fetchone()[0]
      outl_percentage = (greaw_outliers / gre_aw_valid_count * 100) if gre_aw_valid_count > 0 else 0
      print(f".   GRE AW outliers: {greaw_outliers}, Percentage of GPA outliers: {outl_percentage:.2f}%")
      return

