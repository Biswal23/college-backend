from database import SessionLocal, engine, Base
from models import College, Review
from sqlalchemy.exc import IntegrityError, OperationalError

def initialize_database():
    """
    Initialize the database with sample college and review data.
    """
    # Recreate tables to ensure schema is up-to-date
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables recreated successfully")
    except Exception as e:
        print(f"❌ Error recreating database tables: {e}")
        return

    db = SessionLocal()
    try:
        # Check if data already exists to avoid duplicates
        if db.query(College).count() > 0:
            print("✅ Database already initialized with data.")
            return

        # Sample colleges
        colleges = [
            College(
                name="Central Institute of Plastic Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Integrated M.Sc. in Material Science and Engg",
                fees=240000,
                cutoff_min=500506,
                cutoff_max=995058
            ),
            College(
                name="Central Institute of Plastic Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Manufacturing Engineering & Technology",
                fees=240000,
                cutoff_min=480483,
                cutoff_max=1006885
            ),
            College(
                name="Central Institute of Plastic Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Plastic Engineering",
                fees=240004,
                cutoff_min=185541,
                cutoff_max=1105236
            ),
            College(
                name="College of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="B ARCH",
                fees=280000,
                cutoff_min=2018,
                cutoff_max=9799
            ),
            College(
                name="College of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="B. PLAN",
                fees=280000,
                cutoff_min=1331,
                cutoff_max=998798
            ),
            College(
                name="College of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Bio Technology(SSC)",
                fees=280000,
                cutoff_min=104280,
                cutoff_max=234748
            ),
            College(
                name="College of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=280000,
                cutoff_min=76043,
                cutoff_max=197109
            ),
            College(
                name="College of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering(SSC)",
                fees=280000,
                cutoff_min=29654,
                cutoff_max=55566
            ),
            College(
                name="College of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=280000,
                cutoff_min=28548,
                cutoff_max=100288
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Kalahandi",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=80000,
                cutoff_min=209595,
                cutoff_max=389530
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Kalahandi",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=80000,
                cutoff_min=396077,
                cutoff_max=1103800
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Kalahandi",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=80000,
                cutoff_min=399498,
                cutoff_max=1103930
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Keonjhar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=80000,
                cutoff_min=287225,
                cutoff_max=1100049
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Keonjhar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=80000,
                cutoff_min=118741,
                cutoff_max=317462
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Keonjhar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=80000,
                cutoff_min=288459,
                cutoff_max=1101052
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Keonjhar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=80000,
                cutoff_min=214983,
                cutoff_max=968568
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Keonjhar",
                course_level="Btech",
                branch="Metallurgical and Materials Engineering",
                fees=80000,
                cutoff_min=321841,
                cutoff_max=998911
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Keonjhar",
                course_level="Btech",
                branch="Mineral Engineering",
                fees=80000,
                cutoff_min=475293,
                cutoff_max=1104612
            ),
            College(
                name="Government College of Engineering",
                state="Odisha",
                location="Keonjhar",
                course_level="Btech",
                branch="Mining Engineering",
                fees=80000,
                cutoff_min=116246,
                cutoff_max=392350
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Chemical Engineering",
                fees=100000,
                cutoff_min=243932,
                cutoff_max=583695
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=178066,
                cutoff_max=439072
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Computer Science and Engineering(SSC)",
                fees=100000,
                cutoff_min=69372,
                cutoff_max=149276
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=100000,
                cutoff_min=158535,
                cutoff_max=318444
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering(SSC)",
                fees=100000,
                cutoff_min=157980,
                cutoff_max=356370
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=173232,
                cutoff_max=357066
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Metallurgical and Materials Engineering",
                fees=100000,
                cutoff_min=182008,
                cutoff_max=622133
            ),
            College(
                name="Indira Gandhi Institute of Technology",
                state="Odisha",
                location="Sarang",
                course_level="Btech",
                branch="Production Engineering",
                fees=100000,
                cutoff_min=439418,
                cutoff_max=1104027
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Automobile Engineering",
                fees=100000,
                cutoff_min=371704,
                cutoff_max=1104529
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Chemical Engineering",
                fees=100000,
                cutoff_min=509852,
                cutoff_max=1105079
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=154053,
                cutoff_max=1106286
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=101120,
                cutoff_max=228688
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=100000,
                cutoff_min=240845,
                cutoff_max=1102222
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=100000,
                cutoff_min=188545,
                cutoff_max=497701
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=203986,
                cutoff_max=1106001
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Metallurgical and Materials Engineering",
                fees=100000,
                cutoff_min=512697,
                cutoff_max=697117
            ),
            College(
                name="Parala Maharaja Engineering College",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Production Engineering",
                fees=100000,
                cutoff_min=300016,
                cutoff_max=1015340
            ),
            College(
                name="Sambalpur University Institute of Information Technology",
                state="Odisha",
                location="Sambalpur",
                course_level="Btech",
                branch="Computer Science and Engineering(SSC)",
                fees=100000,
                cutoff_min=122971,
                cutoff_max=698114
            ),
            College(
                name="Sambalpur University Institute of Information Technology",
                state="Odisha",
                location="Sambalpur",
                course_level="Btech",
                branch="Electrical and Electronics Engineering(SSC)",
                fees=100000,
                cutoff_min=158193,
                cutoff_max=1102182
            ),
            College(
                name="Sambalpur University Institute of Information Technology",
                state="Odisha",
                location="Sambalpur",
                course_level="Btech",
                branch="Electronics & Communication Engineering(SSC)",
                fees=100000,
                cutoff_min=186923,
                cutoff_max=1101744
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="B ARCH",
                fees=100000,
                cutoff_min=8113,
                cutoff_max=17975
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="B. Tech in Civil Engineering & M.Tech in Structural Engineering (5 year Integrated UG & PG)",
                fees=100000,
                cutoff_min=148075,
                cutoff_max=307873
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="B. Tech in Electrical Engineering & M.Tech in Power System Engineering (5 year Integrated UG & PG)",
                fees=100000,
                cutoff_min=85593,
                cutoff_max=232866
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Chemical Engineering",
                fees=100000,
                cutoff_min=105741,
                cutoff_max=289176
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=115940,
                cutoff_max=226738
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Civil Engineering(SSC)",
                fees=100000,
                cutoff_min=216208,
                cutoff_max=301322
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=43856,
                cutoff_max=67879
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Computer Science and Engineering(SSC)",
                fees=100000,
                cutoff_min=54953,
                cutoff_max=72166
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=100000,
                cutoff_min=41807,
                cutoff_max=113772
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Electrical and Electronics Engineering(SSC)",
                fees=100000,
                cutoff_min=115833,
                cutoff_max=184650
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=100000,
                cutoff_min=32986,
                cutoff_max=173959
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=100000,
                cutoff_min=62600,
                cutoff_max=161504
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Information Technology(SSC)",
                fees=100000,
                cutoff_min=63525,
                cutoff_max=96255
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=51201,
                cutoff_max=179009
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Metallurgical and Materials Engineering",
                fees=100000,
                cutoff_min=174158,
                cutoff_max=364290
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Production Engineering",
                fees=100000,
                cutoff_min=217415,
                cutoff_max=424414
            ),
            College(
                name="Veer Surendra Sai University of Technology",
                state="Odisha",
                location="Burla",
                course_level="Btech",
                branch="Production Engineering(SSC)",
                fees=100000,
                cutoff_min=303638,
                cutoff_max=530495
            ),
            College(
                name="Adarsha College of Engineering",
                state="Odisha",
                location="Angul",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=1000000,
                cutoff_min=540105,
                cutoff_max=581382
            ),
            College(
                name="Ajay Binaya Institute of Technology",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=513118,
                cutoff_max=1106574
            ),
            College(
                name="Ajay Binaya Institute of Technology",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Electrical and Computer Engineering",
                fees=100000,
                cutoff_min=796202,
                cutoff_max=924246
            ),
            College(
                name="Ajay Binaya Institute of Technology",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=100000,
                cutoff_min=1101328,
                cutoff_max=1105634
            ),
            College(
                name="Ajay Binaya Institute of Technology",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=1100461,
                cutoff_max=1104852
            ),
            College(
                name="Aryan Institute of Engineering & Technology",
                state="Odisha",
                location="Barakuda",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=1100362,
                cutoff_max=1104723
            ),
            College(
                name="Aryan Institute of Engineering & Technology",
                state="Odisha",
                location="Barakuda",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=386139,
                cutoff_max=1105240
            ),
            College(
                name="Aryan Institute of Engineering & Technology",
                state="Odisha",
                location="Barakuda",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=100000,
                cutoff_min=789225,
                cutoff_max=1106472
            ),
            College(
                name="Aryan Institute of Engineering & Technology",
                state="Odisha",
                location="Barakuda",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=100000,
                cutoff_min=1102715,
                cutoff_max=1102715
            ),
            College(
                name="Aryan Institute of Engineering & Technology",
                state="Odisha",
                location="Barakuda",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=100000,
                cutoff_min=906717,
                cutoff_max=1105959
            ),
            College(
                name="Aryan Institute of Engineering & Technology",
                state="Odisha",
                location="Barakuda",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=838897,
                cutoff_max=1106102
            ),
            College(
                name="Balasore College of Engineering & Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=955694,
                cutoff_max=955694
            ),
            College(
                name="Balasore College of Engineering & Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=563957,
                cutoff_max=1105902
            ),
            College(
                name="Balasore College of Engineering & Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=100000,
                cutoff_min=443209,
                cutoff_max=443209
            ),
            College(
                name="Balasore College of Engineering & Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=100000,
                cutoff_min=956570,
                cutoff_max=963052
            ),
            College(
                name="Balasore College of Engineering & Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=1103603,
                cutoff_max=1104044
            ),
            College(
                name="Bhadrak Institute of Engineering & Technology",
                state="Odisha",
                location="Bhadrak",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=1104595,
                cutoff_max=1104771
            ),
            College(
                name="Bhadrak Institute of Engineering & Technology",
                state="Odisha",
                location="Bhadrak",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=907096,
                cutoff_max=1106288
            ),
            College(
                name="Bhadrak Institute of Engineering & Technology",
                state="Odisha",
                location="Bhadrak",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=1101527,
                cutoff_max=1104935
            ),
            College(
                name="Bhubaneswar College of Engineering",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=1105232,
                cutoff_max=1105483
            ),
            College(
                name="Bhubaneswar College of Engineering",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=426678,
                cutoff_max=1103513
            ),
            College(
                name="Bhubaneswar College of Engineering",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=100000,
                cutoff_min=943249,
                cutoff_max=995010
            ),
            College(
                name="Bhubaneswar College of Engineering",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=100000,
                cutoff_min=1101569,
                cutoff_max=1102873
            ),
            College(
                name="Bhubaneswar Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Aeronautical Engineering",
                fees=100000,
                cutoff_min=772288,
                cutoff_max=1105552
            ),
            College(
                name="Bhubaneswar Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=653654,
                cutoff_max=1106483
            ),
            College(
                name="Bhubaneswar Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=931299,
                cutoff_max=1106087
            ),
            College(
                name="Bhubaneswar Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=1103817,
                cutoff_max=1106090
            ),
            College(
                name="Bhubaneswar Institute of Industrial Technology",
                state="Odisha",
                location="Retanga",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=1103722,
                cutoff_max=1103722
            ),
            College(
                name="Bhubaneswar Institute of Industrial Technology",
                state="Odisha",
                location="Retanga",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=883661,
                cutoff_max=895536
            ),
            College(
                name="Bhubaneswar Institute of Industrial Technology",
                state="Odisha",
                location="Retanga",
                course_level="Btech",
                branch="Mining Engineering",
                fees=100000,
                cutoff_min=789147,
                cutoff_max=1105126
            ),
            College(
                name="Bhubaneswar Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=100000,
                cutoff_min=1101346,
                cutoff_max=1101816
            ),
            College(
                name="Bhubaneswar Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=975875,
                cutoff_max=1105883
            ),
            College(
                name="Bhubaneswar Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=100000,
                cutoff_min=1105065,
                cutoff_max=1106385
            ),
            College(
                name="Bhubaneswar Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=100000,
                cutoff_min=1105905,
                cutoff_max=1105905
            ),
            College(
                name="Bhubaneswar Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=1103305,
                cutoff_max=1104646
            ),
            College(
                name="Black Diamond College of Engineering and Technology",
                state="Odisha",
                location="Jharsuguda",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=100000,
                cutoff_min=1100596,
                cutoff_max=1106432
            ),
            College(
                name="Black Diamond College of Engineering and Technology",
                state="Odisha",
                location="Jharsuguda",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=100000,
                cutoff_min=727588,
                cutoff_max=1104253
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Chemical Engineering",
                fees=1200000,
                cutoff_min=825309,
                cutoff_max=825309
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=1200000,
                cutoff_min=583696,
                cutoff_max=719149
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Engineering",
                fees=1200000,
                cutoff_min=924445,
                cutoff_max=981328
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Engineering (Software Engg)",
                fees=1200000,
                cutoff_min=385279,
                cutoff_max=1102954
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer science & Engineering (Data Science)",
                fees=1200000,
                cutoff_min=648306,
                cutoff_max=866000
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=1200000,
                cutoff_min=164680,
                cutoff_max=1100020
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering (IoT and Cyber Security Including block chain technology)",
                fees=1200000,
                cutoff_min=573769,
                cutoff_max=573769
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Information Technology",
                fees=1200000,
                cutoff_min=412993,
                cutoff_max=1103619
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science Engineering (Artificial Intelligence and Machine Learning)",
                fees=1200000,
                cutoff_min=340490,
                cutoff_max=1100401
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=1200000,
                cutoff_min=679100,
                cutoff_max=908650
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=1200000,
                cutoff_min=290292,
                cutoff_max=290292
            ),
            College(
                name="C. V. Raman Global University",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=1200000,
                cutoff_min=929068,
                cutoff_max=929068
            ),
            College(
                name="Capital Engineering College",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Civil Engineering",
                fees=1200000,
                cutoff_min=1103035,
                cutoff_max=1104901
            ),
            College(
                name="Capital Engineering College",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=1200000,
                cutoff_min=577755,
                cutoff_max=1104813
            ),
            College(
                name="Capital Engineering College",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=1200000,
                cutoff_min=1100508,
                cutoff_max=1105964
            ),
            College(
                name="Capital Engineering College",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=1200000,
                cutoff_min=1101121,
                cutoff_max=1106471
            ),
            College(
                name="Capital Engineering College",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=1200000,
                cutoff_min=1103988,
                cutoff_max=1105975
            ),
            College(
                name="College of Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=1200000,
                cutoff_min=898022,
                cutoff_max=1015835
            ),
            College(
                name="College of Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=1200000,
                cutoff_min=361740,
                cutoff_max=999936
            ),
            College(
                name="College of Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=1200000,
                cutoff_min=1101534,
                cutoff_max=1101534
            ),
            College(
                name="College of Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=1200000,
                cutoff_min=1105893,
                cutoff_max=1105893
            ),
            College(
                name="DRIEMS",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Civil Engineering",
                fees=1200000,
                cutoff_min=1103902,
                cutoff_max=1106037
            ),
            College(
                name="DRIEMS",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=1200000,
                cutoff_min=672919,
                cutoff_max=1106068
            ),
            College(
                name="DRIEMS",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=1200000,
                cutoff_min=564145,
                cutoff_max=1104706
            ),
            College(
                name="DRIEMS",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=1200000,
                cutoff_min=1100403,
                cutoff_max=1102453
            ),
            College(
                name="DRIEMS",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=1200000,
                cutoff_min=1101714,
                cutoff_max=1101714
            ),
            College(
                name="DRIEMS",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=839978,
                cutoff_max=1105419
            ),
            College(
                name="Eastern Academy of Science and Technology",
                state="Odisha",
                location="Phulanakhara",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=1105302,
                cutoff_max=1106379
            ),
            College(
                name="Eastern Academy of Science and Technology",
                state="Odisha",
                location="Phulanakhara",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=200000,
                cutoff_min=1105176,
                cutoff_max=1106588
            ),
            College(
                name="Eastern Academy of Science and Technology",
                state="Odisha",
                location="Phulanakhara",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=1104406,
                cutoff_max=1104406
            ),
            College(
                name="Einstein Academy of Technology and Management",
                state="Odisha",
                location="Baniatangi",
                course_level="Btech",
                branch="Civil Engineering",
                fees=200000,
                cutoff_min=1007550,
                cutoff_max=1106389
            ),
            College(
                name="Einstein Academy of Technology and Management",
                state="Odisha",
                location="Baniatangi",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=622963,
                cutoff_max=1106347
            ),
            College(
                name="Einstein Academy of Technology and Management",
                state="Odisha",
                location="Baniatangi",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=836319,
                cutoff_max=1106059
            ),
            College(
                name="Gandhi Academy of Technology and Engineering",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Civil Engineering",
                fees=200000,
                cutoff_min=1102227,
                cutoff_max=1104405
            ),
            College(
                name="Gandhi Academy of Technology and Engineering",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=554990,
                cutoff_max=1106530
            ),
            College(
                name="Gandhi Academy of Technology and Engineering",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=200000,
                cutoff_min=1102975,
                cutoff_max=1106257
            ),
            College(
                name="Gandhi Academy of Technology and Engineering",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=200000,
                cutoff_min=416291,
                cutoff_max=1105016
            ),
            College(
                name="Gandhi Academy of Technology and Engineering",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=1101059,
                cutoff_max=1105857
            ),
            College(
                name="Gandhi Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=200000,
                cutoff_min=1103041,
                cutoff_max=1104678
            ),
            College(
                name="Gandhi Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=417675,
                cutoff_max=1105515
            ),
            College(
                name="Gandhi Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical and Computer Engineering",
                fees=200000,
                cutoff_min=837787,
                cutoff_max=1104332
            ),
            College(
                name="Gandhi Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=200000,
                cutoff_min=1105036,
                cutoff_max=1106514
            ),
            College(
                name="Gandhi Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics and Computer Engineering",
                fees=200000,
                cutoff_min=895213,
                cutoff_max=1104239
            ),
            College(
                name="Gandhi Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=754524,
                cutoff_max=1106593
            ),
            College(
                name="Gandhi Institute for Education and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Civil Engineering",
                fees=200000,
                cutoff_min=880599,
                cutoff_max=1106307
            ),
            College(
                name="Gandhi Institute for Education and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=487655,
                cutoff_max=1106447
            ),
            College(
                name="Gandhi Institute for Education and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electrical and Computer Engineering",
                fees=200000,
                cutoff_min=1100397,
                cutoff_max=1106490
            ),
            College(
                name="Gandhi Institute for Education and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=200000,
                cutoff_min=1101000,
                cutoff_max=1105713
            ),
            College(
                name="Gandhi Institute for Education and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=200000,
                cutoff_min=1102858,
                cutoff_max=1106189
            ),
            College(
                name="Gandhi Institute for Education and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=441660,
                cutoff_max=1106350
            ),
            College(
                name="Gandhi Institute for Technology GIFT",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Agriculture Engineering",
                fees=200000,
                cutoff_min=716470,
                cutoff_max=1106567
            ),
            College(
                name="Gandhi Institute for Technology GIFT",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=413034,
                cutoff_max=1105706
            ),
            College(
                name="Gandhi Institute for Technology GIFT",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=829025,
                cutoff_max=829025
            ),
            College(
                name="Gandhi Institute of Advanced Computer and Research",
                state="Odisha",
                location="Raygada",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=1100277,
                cutoff_max=1100277
            ),
            College(
                name="Gandhi Institute of Excellent Technocrats",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=200000,
                cutoff_min=1101724,
                cutoff_max=1101724
            ),
            College(
                name="Gandhi Institute of Excellent Technocrats",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=679924,
                cutoff_max=1106445
            ),
            College(
                name="Gandhi Institute of Excellent Technocrats",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=200000,
                cutoff_min=1021302,
                cutoff_max=1021415
            ),
            College(
                name="Gandhi Institute of Excellent Technocrats",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=200000,
                cutoff_min=146468,
                cutoff_max=1103761
            ),
            College(
                name="Ghanashyama Hemalata Institute of Technology and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=200000,
                cutoff_min=1102880,
                cutoff_max=1102880
            ),
            College(
                name="GIET University",
                state="Odisha",
                location="Gunupur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=849487,
                cutoff_max=849487
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=200000,
                cutoff_min=928257,
                cutoff_max=1105823
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science & Engineering (Artificial Intelligence)",
                fees=200000,
                cutoff_min=360057,
                cutoff_max=1102810
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer science & Engineering (Data Science)",
                fees=200000,
                cutoff_min=474644,
                cutoff_max=1100754
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="COMPUTER SCIENCE & TECHNOLOGY",
                fees=200000,
                cutoff_min=639368,
                cutoff_max=1106238
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=200000,
                cutoff_min=328519,
                cutoff_max=1105789
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Information Technology",
                fees=1000000,
                cutoff_min=428414,
                cutoff_max=1104024
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=1000000,
                cutoff_min=943093,
                cutoff_max=943093
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=1000000,
                cutoff_min=890260,
                cutoff_max=890260
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=1000000,
                cutoff_min=618470,
                cutoff_max=1104084
            ),
            College(
                name="GITA",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=1000000,
                cutoff_min=826770,
                cutoff_max=1105983
            ),
            College(
                name="Gopal Krushna College of Engineering and Technology",
                state="Odisha",
                location="Jeypore",
                course_level="Btech",
                branch="Civil Engineering",
                fees=160000,
                cutoff_min=1101225,
                cutoff_max=1105077
            ),
            College(
                name="Gopal Krushna College of Engineering and Technology",
                state="Odisha",
                location="Jeypore",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=160000,
                cutoff_min=1100775,
                cutoff_max=1103403
            ),
            College(
                name="Gopal Krushna College of Engineering and Technology",
                state="Odisha",
                location="Jeypore",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=160000,
                cutoff_min=1105544,
                cutoff_max=1105544
            ),
            College(
                name="Hi-Tech Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=220000,
                cutoff_min=1102379,
                cutoff_max=1106152
            ),
            College(
                name="Hi-Tech Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=220000,
                cutoff_min=605531,
                cutoff_max=1106119
            ),
            College(
                name="Hi-Tech Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=220000,
                cutoff_min=1100975,
                cutoff_max=1100975
            ),
            College(
                name="Hi-Tech Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=220000,
                cutoff_min=979431,
                cutoff_max=1106340
            ),
            College(
                name="Indotech College of Engineering",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Civil Engineering",
                fees=220000,
                cutoff_min=1101093,
                cutoff_max=1101093
            ),
            College(
                name="Indus College of Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=220000,
                cutoff_min=1104400,
                cutoff_max=1104400
            ),
            College(
                name="Indus College of Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=220000,
                cutoff_min=1102301,
                cutoff_max=1104930
            ),
            College(
                name="Jagannath Institute of Engineering and Technology",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=220000,
                cutoff_min=644480,
                cutoff_max=644480
            ),
            College(
                name="Jagannath Institute of Engineering and Technology",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=220000,
                cutoff_min=1104937,
                cutoff_max=1104937
            ),
            College(
                name="Kalam Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Civil Engineering",
                fees=220000,
                cutoff_min=1105392,
                cutoff_max=1106448
            ),
            College(
                name="Kalam Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=220000,
                cutoff_min=931325,
                cutoff_max=1106187
            ),
            College(
                name="Kalam Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=220000,
                cutoff_min=1101010,
                cutoff_max=1106027
            ),
            College(
                name="Kalam Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=220000,
                cutoff_min=491062,
                cutoff_max=1105625
            ),
            College(
                name="KMBB College of Engineering and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=220000,
                cutoff_min=540487,
                cutoff_max=1105864
            ),
            College(
                name="KMBB College of Engineering and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=220000,
                cutoff_min=679546,
                cutoff_max=679546
            ),
            College(
                name="KMBB College of Engineering and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=220000,
                cutoff_min=1101413,
                cutoff_max=1103389
            ),
            College(
                name="KMBB College of Engineering and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=220000,
                cutoff_min=1100346,
                cutoff_max=1100346
            ),
            College(
                name="KMBB College of Engineering and Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=220000,
                cutoff_min=1103888,
                cutoff_max=1106039
            ),
            College(
                name="Konark Institute of Science and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=220000,
                cutoff_min=399692,
                cutoff_max=1106057
            ),
            College(
                name="Konark Institute of Science and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=220000,
                cutoff_min=376840,
                cutoff_max=1105814
            ),
            College(
                name="Konark Institute of Science and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=220000,
                cutoff_min=1101089,
                cutoff_max=1101089
            ),
            College(
                name="Konark Institute of Science and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=220000,
                cutoff_min=943697,
                cutoff_max=1106551
            ),
            College(
                name="Konark Institute of Science and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=220000,
                cutoff_min=185534,
                cutoff_max=1106441
            ),
            College(
                name="Mahavir Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=220000,
                cutoff_min=1102725,
                cutoff_max=1105666
            ),
            College(
                name="Mahavir Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=220000,
                cutoff_min=1100999,
                cutoff_max=1100999
            ),
            College(
                name="Mahavir Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=220000,
                cutoff_min=1102005,
                cutoff_max=1104372
            ),
            College(
                name="Mahavir Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Information Technology",
                fees=220000,
                cutoff_min=1103772,
                cutoff_max=1103772
            ),
            College(
                name="Mahavir Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=220000,
                cutoff_min=1106512,
                cutoff_max=1106512
            ),
            College(
                name="Majhighariani Institute of Technology and Science",
                state="Odisha",
                location="Rayagada",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=144000,
                cutoff_min=1101004,
                cutoff_max=1101004
            ),
            College(
                name="Modern Engineering and Management Studies",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=738105,
                cutoff_max=1106038
            ),
            College(
                name="Modern Engineering and Management Studies",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1106392,
                cutoff_max=1106392
            ),
            College(
                name="Modern Engineering and Management Studies",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=144000,
                cutoff_min=1102406,
                cutoff_max=1105273
            ),
            College(
                name="Modern Engineering and Management Studies",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electronics & Instrumentation Engineering",
                fees=144000,
                cutoff_min=1100861,
                cutoff_max=1104373
            ),
            College(
                name="Modern Institute of Technology and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=1103925,
                cutoff_max=1103925
            ),
            College(
                name="Modern Institute of Technology and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=870242,
                cutoff_max=1105670
            ),
            College(
                name="Modern Institute of Technology and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=144000,
                cutoff_min=1105008,
                cutoff_max=1105008
            ),
            College(
                name="Modern Institute of Technology and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1106579,
                cutoff_max=1106579
            ),
            College(
                name="Nalanda Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=762002,
                cutoff_max=1106415
            ),
            College(
                name="Nalanda Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=475343,
                cutoff_max=1105925
            ),
            College(
                name="Nalanda Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=836779,
                cutoff_max=1106525
            ),
            College(
                name="Nalanda Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=727698,
                cutoff_max=1106550
            ),
            College(
                name="National Institute of Science and Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Civil Engineering",
                fees=232000,
                cutoff_min=1103211,
                cutoff_max=1103211
            ),
            College(
                name="National Institute of Science and Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=232000,
                cutoff_min=306747,
                cutoff_max=1104559
            ),
            College(
                name="National Institute of Science and Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering(2nd shift)",
                fees=232000,
                cutoff_min=587374,
                cutoff_max=1105374
            ),
            College(
                name="National Institute of Science and Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=232000,
                cutoff_min=896267,
                cutoff_max=896267
            ),
            College(
                name="National Institute of Science and Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=232000,
                cutoff_min=516780,
                cutoff_max=1102879
            ),
            College(
                name="National Institute of Science and Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Information Technology",
                fees=232000,
                cutoff_min=604882,
                cutoff_max=969821
            ),
            College(
                name="National Institute of Science and Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=232000,
                cutoff_min=955513,
                cutoff_max=955513
            ),
            College(
                name="NM Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=232000,
                cutoff_min=988948,
                cutoff_max=1105781
            ),
            College(
                name="NM Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=232000,
                cutoff_min=953572,
                cutoff_max=1105524
            ),
            College(
                name="NM Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=232000,
                cutoff_min=1105538,
                cutoff_max=1105538
            ),
            College(
                name="NM Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=232000,
                cutoff_min=874080,
                cutoff_max=1106109
            ),
            College(
                name="Oxford College of Engineering and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=232000,
                cutoff_min=1104717,
                cutoff_max=1106535
            ),
            College(
                name="Oxford College of Engineering and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=232000,
                cutoff_min=850302,
                cutoff_max=1106050
            ),
            College(
                name="Oxford College of Engineering and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=232000,
                cutoff_min=1103520,
                cutoff_max=1103520
            ),
            College(
                name="Oxford College of Engineering and Management",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=232000,
                cutoff_min=1104907,
                cutoff_max=1104962
            ),
            College(
                name="Padmashree Krutartha Acharya College of Engineering",
                state="Odisha",
                location="Bargarh",
                course_level="Btech",
                branch="Civil Engineering",
                fees=232000,
                cutoff_min=1100474,
                cutoff_max=1105819
            ),
            College(
                name="Padmashree Krutartha Acharya College of Engineering",
                state="Odisha",
                location="Bargarh",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=232000,
                cutoff_min=1101035,
                cutoff_max=1106456
            ),
            College(
                name="Padmashree Krutartha Acharya College of Engineering",
                state="Odisha",
                location="Bargarh",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=232000,
                cutoff_min=1100321,
                cutoff_max=1103968
            ),
            College(
                name="Piloo Modi College of Architecture",
                state="Odisha",
                location="Cuttack",
                course_level="Btech",
                branch="B ARCH",
                fees=232000,
                cutoff_min=16872,
                cutoff_max=137341
            ),
            College(
                name="Raajdhani Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=232000,
                cutoff_min=943579,
                cutoff_max=1105074
            ),
            College(
                name="Raajdhani Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=232000,
                cutoff_min=596445,
                cutoff_max=1106280
            ),
            College(
                name="Raajdhani Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=232000,
                cutoff_min=1101271,
                cutoff_max=1106503
            ),
            College(
                name="Raajdhani Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=232000,
                cutoff_min=1106071,
                cutoff_max=1106071
            ),
            College(
                name="Raajdhani Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=232000,
                cutoff_min=1101295,
                cutoff_max=1106161
            ),
            College(
                name="Radha Krishna Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=140000,
                cutoff_min=1100160,
                cutoff_max=1105313
            ),
            College(
                name="Radha Krishna Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=140000,
                cutoff_min=775121,
                cutoff_max=1106571
            ),
            College(
                name="Radha Krishna Institute of Engineering and Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=140000,
                cutoff_min=1105816,
                cutoff_max=1105816
            ),
            College(
                name="Rayagada Institute of Technology & Management",
                state="Odisha",
                location="Rayagada",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=140000,
                cutoff_min=1100782,
                cutoff_max=1100782
            ),
            College(
                name="Roland Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=140000,
                cutoff_min=581519,
                cutoff_max=1104867
            ),
            College(
                name="Roland Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=140000,
                cutoff_min=1103097,
                cutoff_max=1105837
            ),
            College(
                name="Roland Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=140000,
                cutoff_min=1104164,
                cutoff_max=1105797
            ),
            College(
                name="Sanjaya Memorial Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Civil Engineering",
                fees=140000,
                cutoff_min=1101641,
                cutoff_max=1106263
            ),
            College(
                name="Sanjaya Memorial Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=140000,
                cutoff_min=892166,
                cutoff_max=1106557
            ),
            College(
                name="Sanjaya Memorial Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=140000,
                cutoff_min=1100766,
                cutoff_max=1102748
            ),
            College(
                name="Sanjaya Memorial Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=140000,
                cutoff_min=1100254,
                cutoff_max=1106358
            ),
            College(
                name="Sanjaya Memorial Institute of Technology",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=140000,
                cutoff_min=1105175,
                cutoff_max=1105484
            ),
            College(
                name="Seemanta Engineering College",
                state="Odisha",
                location="Jharpokharia",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=140000,
                cutoff_min=1104417,
                cutoff_max=1104765
            ),
            College(
                name="Seemanta Engineering College",
                state="Odisha",
                location="Jharpokharia",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=144000,
                cutoff_min=1100159,
                cutoff_max=1105161
            ),
            College(
                name="Seemanta Engineering College",
                state="Odisha",
                location="Jharpokharia",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1102175,
                cutoff_max=1105148
            ),
            College(
                name="SGI School of Architecture",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="B ARCH",
                fees=144000,
                cutoff_min=116602,
                cutoff_max=127843
            ),
            College(
                name="Shibani Institute of Technical Education",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=924143,
                cutoff_max=924143
            ),
            College(
                name="Shibani Institute of Technical Education",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=1100664,
                cutoff_max=1106488
            ),
            College(
                name="Shibani Institute of Technical Education",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1102022,
                cutoff_max=1103329
            ),
            # Sample colleges
        
            College(
                name="Shibani Institute of Technical Education",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1102022,
                cutoff_max=1103329
            ),
            College(
                name="Shibani Institute of Technical Education",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1103868,
                cutoff_max=1105100
            ),
            College(
                name="Silicon Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Engineering",
                fees=144000,
                cutoff_min=280843,
                cutoff_max=874209
            ),
            College(
                name="Silicon Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="COMPUTER SCIENCE & TECHNOLOGY",
                fees=144000,
                cutoff_min=230983,
                cutoff_max=589120
            ),
            College(
                name="Silicon Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=124702,
                cutoff_max=317193
            ),
            College(
                name="Silicon Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=144000,
                cutoff_min=365270,
                cutoff_max=1100506
            ),
            College(
                name="Silicon Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=144000,
                cutoff_min=263422,
                cutoff_max=1105150
            ),
            College(
                name="Silicon Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Instrumentation Engineering",
                fees=144000,
                cutoff_min=864022,
                cutoff_max=864022
            ),
            College(
                name="Sophitorium Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=1100092,
                cutoff_max=1106528
            ),
            College(
                name="Sophitorium Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=1103224,
                cutoff_max=1106081
            ),
            College(
                name="Sophitorium Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1103193,
                cutoff_max=1106276
            ),
            College(
                name="Sophitorium Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=144000,
                cutoff_min=1100904,
                cutoff_max=1100904
            ),
            College(
                name="Sophitorium Engineering College",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1100099,
                cutoff_max=1106603
            ),
            College(
                name="Spintronic Technology and Advance Research",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=1105658,
                cutoff_max=1105658
            ),
            College(
                name="Spintronic Technology and Advance Research",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=1104528,
                cutoff_max=1106515
            ),
            College(
                name="Spintronic Technology and Advance Research",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=540269,
                cutoff_max=1105859
            ),
            College(
                name="Srinix College of Engineering",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=1106362,
                cutoff_max=1106362
            ),
            College(
                name="Srinix College of Engineering",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=640142,
                cutoff_max=1106605
            ),
            College(
                name="Srinix College of Engineering",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=144000,
                cutoff_min=1103377,
                cutoff_max=1104772
            ),
            College(
                name="Srinix College of Engineering",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1100485,
                cutoff_max=1106417
            ),
            College(
                name="Srinix College of Engineering",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1101220,
                cutoff_max=1106536
            ),
            College(
                name="Suddhananda Engineering and Research Centre",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=1104132,
                cutoff_max=1104132
            ),
            College(
                name="Suddhananda Engineering and Research Centre",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1101546,
                cutoff_max=1102714
            ),
            College(
                name="Suddhananda Engineering and Research Centre",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1104103,
                cutoff_max=1105488
            ),
            College(
                name="Sundergarh Engineering College",
                state="Odisha",
                location="Sundergarh",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=1105431,
                cutoff_max=1105431
            ),
            College(
                name="Sundergarh Engineering College",
                state="Odisha",
                location="Sundergarh",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1100247,
                cutoff_max=1100247
            ),
            College(
                name="Sundergarh Engineering College",
                state="Odisha",
                location="Sundergarh",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1105774,
                cutoff_max=1105774
            ),
            College(
                name="Synergy Institute of Engineering and Technology",
                state="Odisha",
                location="Dhenkanal",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=555708,
                cutoff_max=1012973
            ),
            College(
                name="Synergy Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=552036,
                cutoff_max=990156
            ),
            College(
                name="Synergy Institute of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1103333,
                cutoff_max=1103333
            ),
            College(
                name="Temple City Institute of Technology and Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=1105691,
                cutoff_max=1105918
            ),
            College(
                name="Temple City Institute of Technology and Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=895040,
                cutoff_max=1106031
            ),
            College(
                name="Temple City Institute of Technology and Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=1103623,
                cutoff_max=1106569
            ),
            College(
                name="Temple City Institute of Technology and Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Communication Engineering",
                fees=144000,
                cutoff_min=1105993,
                cutoff_max=1105993
            ),
            College(
                name="Temple City Institute of Technology and Engineering",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1102008,
                cutoff_max=1102124
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=1014263,
                cutoff_max=1014263
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="COMPUTER SCIENCE & TECHNOLOGY",
                fees=144000,
                cutoff_min=644873,
                cutoff_max=1102697
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=354160,
                cutoff_max=1105578
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science and Information Technology",
                fees=144000,
                cutoff_min=789912,
                cutoff_max=1103421
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Computer Science Engineering (Artificial Intelligence and Machine Learning)",
                fees=144000,
                cutoff_min=560710,
                cutoff_max=989896
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electrical Engineering",
                fees=144000,
                cutoff_min=979452,
                cutoff_max=979452
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=144000,
                cutoff_min=428973,
                cutoff_max=1102633
            ),
            College(
                name="Trident Academy of Technology",
                state="Odisha",
                location="Bhubaneswar",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=810649,
                cutoff_max=810649
            ),
            College(
                name="Vedang Institute of Technology",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Metallurgical Engineering",
                fees=144000,
                cutoff_min=1106137,
                cutoff_max=1106137
            ),
            College(
                name="Vignan Institute of Technology and Management",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=524103,
                cutoff_max=1105788
            ),
            College(
                name="Vignan Institute of Technology and Management",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=144000,
                cutoff_min=1100233,
                cutoff_max=1104762
            ),
            College(
                name="Vignan Institute of Technology and Management",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Electronics & Telecommunication Engineering",
                fees=144000,
                cutoff_min=1103928,
                cutoff_max=1103928
            ),
            College(
                name="Vignan Institute of Technology and Management",
                state="Odisha",
                location="Berhampur",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1101627,
                cutoff_max=1105341
            ),
            College(
                name="Vijayanjali Institute of Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=845810,
                cutoff_max=850395
            ),
            College(
                name="Vijayanjali Institute of Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=144000,
                cutoff_min=362054,
                cutoff_max=1103595
            ),
            College(
                name="Vijayanjali Institute of Technology",
                state="Odisha",
                location="Balasore",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=723103,
                cutoff_max=1100646
            ),
            College(
                name="Vikash Institute of Technology",
                state="Odisha",
                location="BARGARH",
                course_level="Btech",
                branch="Civil Engineering",
                fees=144000,
                cutoff_min=838739,
                cutoff_max=838739
            ),
            College(
                name="Vikash Institute of Technology",
                state="Odisha",
                location="BARGARH",
                course_level="Btech",
                branch="Computer Science and Engineering",
                fees=144000,
                cutoff_min=869692,
                cutoff_max=1105677
            ),
            College(
                name="Vikash Institute of Technology",
                state="Odisha",
                location="BARGARH",
                course_level="Btech",
                branch="Electrical and Electronics Engineering",
                fees=144000,
                cutoff_min=1102080,
                cutoff_max=1103932
            ),
            College(
                name="Vikash Institute of Technology",
                state="Odisha",
                location="BARGARH",
                course_level="Btech",
                branch="Integrated MSc in Applied Chemistry",
                fees=144000,
                cutoff_min=230359,
                cutoff_max=230359
            ),
            College(
                name="Vikash Institute of Technology",
                state="Odisha",
                location="BARGARH",
                course_level="Btech",
                branch="Integrated MSc in Applied Physics",
                fees=144000,
                cutoff_min=634537,
                cutoff_max=1006554
            ),
            College(
                name="Vikash Institute of Technology",
                state="Odisha",
                location="BARGARH",
                course_level="Btech",
                branch="Integrated MSc in Mathematics and Computing",
                fees=144000,
                cutoff_min=440803,
                cutoff_max=440803
            ),
            College(
                name="Vikash Institute of Technology",
                state="Odisha",
                location="BARGARH",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=214917,
                cutoff_max=214917
            ),
            College(
                name="VITS Engineering College",
                state="Odisha",
                location="Khurda",
                course_level="Btech",
                branch="Mechanical Engineering",
                fees=144000,
                cutoff_min=1104015,
                cutoff_max=1104015
            )
        ]

        # Add colleges to the session
        db.add_all(colleges)
        db.commit()
        print("✅ Sample colleges added successfully")
    except IntegrityError as e:
        db.rollback()
        print(f"❌ IntegrityError: {e}")
    except OperationalError as e:
        db.rollback()
        print(f"❌ OperationalError: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding colleges: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
