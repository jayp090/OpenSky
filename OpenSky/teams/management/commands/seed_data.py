"""
Management command: python manage.py seed_data [--clear]
Populates the database with Sky Engineering registry data.
Use --clear to wipe existing data before seeding.
"""
from django.core.management.base import BaseCommand
from teams.models import Department, Team, TeamMember, Skill

MEMBERS_POOL = [
    ("Aisha Patel", "Senior Engineer"), ("Ben Okafor", "Software Engineer"),
    ("Clara Yuen", "Principal Engineer"), ("David Nkosi", "Staff Engineer"),
    ("Elena Vasquez", "Lead Engineer"), ("Finn McCarthy", "QA Engineer"),
    ("Grace Adeyemi", "DevOps Engineer"), ("Hassan Al-Rashid", "Backend Engineer"),
    ("Imogen Clarke", "Frontend Engineer"), ("James Obi", "Software Engineer"),
    ("Kiran Sharma", "Senior Engineer"), ("Lena Braun", "Principal Engineer"),
    ("Marco Rivera", "Staff Engineer"), ("Natasha Ivanova", "QA Engineer"),
    ("Owen Fletcher", "DevOps Engineer"), ("Priya Singh", "Senior Engineer"),
    ("Quentin Dubois", "Backend Engineer"), ("Rachel Okonkwo", "Frontend Engineer"),
    ("Samuel Teo", "Software Engineer"), ("Tanya Volkov", "Lead Engineer"),
    ("Umar Farooq", "Senior Engineer"), ("Vera Andersen", "Principal Engineer"),
    ("Will Nakamura", "Staff Engineer"), ("Xena Papadopoulos", "QA Engineer"),
    ("Yusuf Abubakar", "DevOps Engineer"), ("Zara Mitchell", "Software Engineer"),
    ("Aaron Petrov", "Backend Engineer"), ("Bianca Santos", "Frontend Engineer"),
    ("Carlos Mendez", "Senior Engineer"), ("Diana Walsh", "Lead Engineer"),
    ("Edward Kim", "Software Engineer"), ("Fatima Hassan", "QA Engineer"),
    ("George Larsson", "DevOps Engineer"), ("Hana Watanabe", "Principal Engineer"),
    ("Ivan Kowalski", "Staff Engineer"), ("Julia Ferreira", "Backend Engineer"),
]


def email_from_name(name):
    parts = name.lower().split()
    return f"{parts[0]}.{parts[-1]}@sky.uk"


def assign_members(team, pool_slice):
    for full_name, role in pool_slice:
        email = email_from_name(full_name)
        if not TeamMember.objects.filter(team=team, email=email).exists():
            TeamMember.objects.create(team=team, full_name=full_name, role=role, email=email)


class Command(BaseCommand):
    help = 'Seed the database with Sky Engineering registry data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            TeamMember.objects.all().delete()
            Team.objects.all().delete()
            Department.objects.all().delete()
            Skill.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing data.'))

        # ── Departments ────────────────────────────────────────
        dept_data = [
            ('xTV_Web', 'Sebastian Holt',
             'Responsible for the xTV Web platform — client-side engineering, frontend and backend systems for Sky\'s web TV experience.'),
            ('Native TVs', 'Mason Briggs',
             'Engineers building native TV applications for Roku, Apple TV and other connected TV platforms.'),
            ('Mobile', 'Violet Ramsey',
             'Cross-platform mobile engineering teams delivering Sky\'s iOS and Android applications.'),
            ('Reliability_Tool', 'Lucy Vaughn',
             'Site reliability, tooling, automation and quality engineering across Sky\'s engineering estate.'),
            ('Arch', 'Theodore Knox',
             'Architecture and platform engineering — defining standards, patterns and shared infrastructure.'),
            ('Programme', 'Bella Monroe',
             'Programme-level engineering coordination, advanced research and quantum computing initiatives.'),
        ]
        depts = {}
        for name, head, desc in dept_data:
            dept, _ = Department.objects.get_or_create(name=name, defaults={'head': head, 'description': desc})
            depts[name] = dept
            self.stdout.write(f'  Dept: {name}')

        # ── Teams ──────────────────────────────────────────────
        # (dept_key, name, manager, purpose, channel, github_url, skills_csv, downstream_names_list)
        teams_raw = [
            ('xTV_Web', 'Code Warriors', 'Olivia Carter',
             'Infrastructure scalability, CI/CD integration, and platform resilience for the xTV Web platform.',
             '#xtvweb-code-warriors', 'https://tiny.cc/x9b4t',
             'AWS/GCP,Terraform,Kubernetes,CI/CD,Docker,Python,Bash',
             ['The Debuggers']),
            ('xTV_Web', 'The Debuggers', 'James Bennett',
             'Advanced debugging tools, automated error detection and root cause analysis across Sky services.',
             '#xtvweb-debuggers', 'https://bit.ly/3FgTzX',
             'Debugging Tools (GDB/LLDB),Stack Traces,Log Analysis,Python,Java',
             ['Bit Masters']),
            ('xTV_Web', 'Bit Masters', 'Emma Richardson',
             'Security compliance, encryption techniques and data integrity for xTV Web.',
             '#xtvweb-bit-masters', 'https://t.ly/8YpQm',
             'Cryptography,Penetration Testing,Security Compliance (ISO 27001)',
             ['API Avengers']),
            ('xTV_Web', 'Agile Avengers', 'Benjamin Hayes',
             'Agile transformation, workflow optimisation and lean process improvement across engineering.',
             '#peacock-bravo, #gst-xtv-commerce, #gst-xtv-bravo-frontdoor', 'https://goo.gl/R2X7Pd',
             'Scrum,SAFe,Kanban,Jira,Miro,Confluence',
             ['The Sprint Kings']),
            ('xTV_Web', 'Syntax Squad', 'Sophia Mitchell',
             'Automated deployment pipelines, release management and rollback strategies.',
             '#xtvweb-syntax-squad', 'https://tinyurl.com/y7n3lxp2',
             'CI/CD,GitHub Actions,Jenkins,YAML,Kubernetes,Helm Charts',
             ['The Feature Crafters']),
            ('xTV_Web', 'The Codebreakers', 'William Cooper',
             'Cryptographic security, authentication protocols and secure API development.',
             '#xtvweb-codebreakers', 'https://bit.do/rJ4mT',
             'Cybersecurity,Ethical Hacking,Encryption (AES/RSA),SSL/TLS',
             ['The Encryption Squad']),
            ('xTV_Web', 'DevOps Dynasty', 'Isabella Ross',
             'DevOps best practices, Kubernetes orchestration and cloud automation.',
             '#xtvweb-devops-dynasty', 'https://is.gd/Kp4XQ9',
             'Kubernetes,Terraform,Ansible,CI/CD,AWS/GCP,Docker,Linux',
             ['Code Warriors']),
            ('xTV_Web', 'Byte Force', 'Elijah Parker',
             'Cloud infrastructure, API gateway development and serverless architecture.',
             '#xtvweb-byte-force', 'https://short.io/L2rYQ5',
             'AWS Lambda,API Gateway,Microservices,GraphQL,Node.js,Go',
             ['API Avengers']),
            ('xTV_Web', 'The Cloud Architects', 'Ava Sullivan',
             'Cloud-native applications, distributed systems and multi-region deployments.',
             '#xtvweb-cloud-architects', 'https://tiny.cc/mQ7nX8',
             'Kubernetes,Istio,Terraform,AWS/GCP/Azure,Load Balancing',
             ['Byte Force', 'Cache Me Outside']),
            ('xTV_Web', 'Full Stack Ninjas', 'Noah Campbell',
             'Frontend and backend synchronisation, API integration and UX/UI consistency.',
             '#xtvweb-fullstack-ninjas', 'https://bit.ly/4Yx9TmR',
             'React,Node.js,TypeScript,GraphQL,Next.js,Django,REST APIs',
             ['The API Explorers']),
            ('xTV_Web', 'The Error Handlers', 'Mia Henderson',
             'Log aggregation, AI-driven anomaly detection and real-time monitoring.',
             '#xtvweb-error-handlers', 'https://t.ly/xM7p9Q',
             'ELK Stack,Splunk,Datadog,New Relic,Exception Handling',
             ['The Debuggers']),
            ('xTV_Web', 'Stack Overflow Survivors', 'Lucas Foster',
             'Knowledge management, engineering playbooks and documentation automation.',
             '#xtvweb-sos', 'https://goo.gl/YX34Pn',
             'Technical Documentation,Knowledge Sharing,Confluence,AI Bots',
             ['The Scrum Lords']),
            ('xTV_Web', 'The Binary Beasts', 'Charlotte Murphy',
             'High-performance computing, low-latency data processing and algorithm efficiency.',
             '#xtvweb-binary-beasts', 'https://tinyurl.com/98tXmLp',
             'C/C++,Data Structures,Parallel Computing,GPU Programming',
             ['The Algorithm Alliance']),
            ('xTV_Web', 'API Avengers', 'Henry Ward',
             'API security, authentication layers and API scalability for Sky services.',
             '#xtvweb-api-avengers', 'https://bit.do/ZpL4TQ',
             'API Security,OAuth,JWT,Postman,OpenAPI/Swagger,REST,gRPC',
             ['The Dev Dragons']),
            ('xTV_Web', 'The Algorithm Alliance', 'Amelia Brooks',
             'Machine learning models, AI-driven analytics and data science applications.',
             '#xtvweb-algorithm-alliance', 'https://is.gd/QxN7T9',
             'Machine Learning,Data Science,Pandas,NumPy,Scikit-learn',
             ['The Codebreakers']),
            # Native TVs
            ('Native TVs', 'Data Wranglers', 'Alexander Perry',
             'Big data engineering, real-time data streaming and database optimisation.',
             '#nativetv-data-wranglers', 'https://short.io/7LpX4YQ',
             'SQL,NoSQL,Hadoop,Spark,Kafka,Python,ETL',
             ['The Bit Manipulators']),
            ('Native TVs', 'The Sprint Kings', 'Evelyn Hughes',
             'Agile backlog management, sprint retrospectives and delivery forecasting.',
             '#nativetv-sprint-kings', 'https://tiny.cc/QpM74X',
             'Agile Methodologies,Jira,Velocity Metrics,Sprint Planning',
             ['The Agile Alchemists']),
            ('Native TVs', 'Exception Catchers', 'Daniel Scott',
             'Fault tolerance, system resilience and disaster recovery planning.',
             '#nativetv-exception-catchers', 'https://bit.ly/X7pL4TQ',
             'Fault Tolerance,Failover Strategies,Incident Response,SRE',
             ['The Debuggers']),
            ('Native TVs', 'Code Monkeys', 'Harper Lewis',
             'Patch deployment, rollback automation and version control best practices.',
             '#nativetv-code-monkeys', 'https://t.ly/M98X7TQ',
             'Git,Hotfix Management,Patch Deployment,Bash,CI/CD',
             ['The Version Controllers']),
            ('Native TVs', 'The Compile Crew', 'Matthew Reed',
             'Compiler optimisation, static code analysis and build system improvements.',
             '#nativetv-compile-crew', 'https://goo.gl/LpX7TQ9',
             'Bazel,CMake,Make,Compiler Optimisation',
             ['The Bit Manipulators']),
            ('Native TVs', 'Git Good', 'Scarlett Edwards',
             'Branching strategies, merge conflict resolution and Git best practices.',
             '#nativetv-git-good', 'https://tinyurl.com/YXpM749',
             'Git,GitOps,Merge Strategies,Branching Models,GitLab CI/CD',
             ['The Version Controllers']),
            ('Native TVs', 'The CI/CD Squad', 'Jack Turner',
             'Continuous integration, automated testing and deployment pipelines.',
             '#nativetv-cicd-squad', 'https://bit.do/QX74MT9',
             'Jenkins,GitHub Actions,GitOps,Terraform,AWS CodePipeline',
             ['Syntax Squad']),
            ('Native TVs', 'Bug Exterminators', 'Lily Phillips',
             'Performance profiling, automated test generation and security patching.',
             '#private-bug-exterminators', 'https://is.gd/MX74TQ9',
             'Test Automation (Selenium/Cypress),Load Testing (JMeter)',
             ['The Debuggers']),
            ('Native TVs', 'The Agile Alchemists', 'Samuel Morgan',
             'Agile maturity assessments, coaching & mentorship, SAFe/LeSS frameworks.',
             '#nativetv-agile-alchemists', 'https://short.io/T9Q7MX4',
             'Agile Transformation,SAFe,Jira,Value Stream Mapping',
             ['Stack Overflow Survivors']),
            ('Native TVs', 'The Hotfix Heroes', 'Grace Patterson',
             'Emergency response, rollback strategies and live system debugging.',
             '#nativetv-hotfix-heroes', 'https://tiny.cc/X7T9Q4M',
             'Real-time Debugging,Rollback Automation,Patch Deployment',
             ['The CI/CD Squad', 'Code Monkeys']),
            # Mobile
            ('Mobile', 'Cache Me Outside', 'Owen Barnes',
             'Caching strategies, distributed cache systems and database query optimisation.',
             '#mobile-cache-me-outside', 'https://bit.ly/74QMXT9',
             'Redis,Memcached,CDN Caching,Cache Invalidation Strategies',
             ['The UX Wizards']),
            ('Mobile', 'The Scrum Lords', 'Chloe Hall',
             'Agile training, sprint planning automation and process governance.',
             '#mobile-scrum-lords', 'https://t.ly/QX7M94T',
             'Scrum Mastery,Agile Coaching,Jira,Retrospective Analysis',
             ['The Sprint Kings', 'Agile Avengers']),
            ('Mobile', 'The 404 Not Found', 'Nathan Fisher',
             'Error page personalisation, debugging-as-a-service and incident response.',
             '#mobile-404-not-found', 'https://goo.gl/T9XQ74M',
             'Incident Response,HTTP Error Handling,Observability',
             ['The Scrum Lords']),
            ('Mobile', 'The Version Controllers', 'Zoey Stevens',
             'GitOps workflows, repository security and automated versioning.',
             '#mobile-version-controllers', 'https://tinyurl.com/X74MT9Q',
             'Git,Repository Management,DevSecOps,GitOps',
             ['The Compile Crew', 'The 404 Not Found']),
            ('Mobile', 'DevNull Pioneers', 'Caleb Bryant',
             'Logging frameworks, observability enhancements and error handling APIs.',
             '#mobile-devnull-pioneers', 'https://bit.do/TQX794M',
             'Logging Systems,Grafana,Prometheus,Observability',
             ['The API Explorers']),
            ('Mobile', 'The Code Refactors', 'Hannah Simmons',
             'Code maintainability, tech debt reduction and automated refactoring tools.',
             '#gst-mobile-commerce-poker-face', 'https://is.gd/MTX974Q',
             'Code Cleanup,Tech Debt Management,SonarQube,Refactoring',
             ['Bug Exterminators']),
            ('Mobile', 'The Jenkins Juggernauts', 'Isaac Jenkins',
             'CI/CD pipeline optimisation, Jenkins plugin development and infrastructure as code.',
             '#mobile-jenkins-juggernauts', 'https://short.io/9X74TQM',
             'CI/CD Pipelines,Jenkins Scripting,Kubernetes,YAML',
             ['DevOps Dynasty', 'Git Good']),
            ('Mobile', 'Infinite Loopers', 'Madison Clarke',
             'Frontend performance optimisation, UI/UX consistency and component reusability.',
             '#mobile-infinite-loopers', 'https://tiny.cc/QMTX749',
             'Frontend Optimisation,Performance Metrics,JavaScript,CSS',
             ['The Feature Crafters']),
            ('Mobile', 'The Feature Crafters', 'Gabriel Coleman',
             'Feature flagging, A/B testing automation and rapid prototyping.',
             '#mobile-feature-crafters', 'https://bit.ly/X7Q9T4M',
             'A/B Testing,Feature Flagging,Frontend Frameworks',
             ['The Error Handlers', 'Syntax Squad']),
            ('Mobile', 'The Bit Manipulators', 'Riley Sanders',
             'Binary data processing, encoding/decoding algorithms and compression techniques.',
             '#mobile-bit-manipulators', 'https://t.ly/MTQX794',
             'Bitwise Operations,Low-level Optimisation,Assembly,C++',
             ['The Binary Beasts']),
            ('Mobile', 'Kernel Crushers', 'Leo Watson',
             'Low-level optimisation, OS kernel tuning and hardware acceleration.',
             '#mobile-kernel-crushers', 'https://goo.gl/7QXMT49',
             'Linux Kernel Development,System Performance,Rust,C',
             ['The API Avengers']),
            ('Mobile', 'The Git Masters', 'Victoria Price',
             'Git automation, monorepo strategies and repository analytics.',
             '#mobile-git-masters', 'https://tinyurl.com/MTX749Q',
             'GitOps,Repository Scaling,Git Automation',
             ['The Version Controllers']),
            ('Mobile', 'The API Explorers', 'Julian Bell',
             'API documentation, API analytics and developer experience optimisation.',
             '#mobile-api-explorers', 'https://bit.do/X7TQ49M',
             'API Testing (Postman/Swagger),API Gateway Management',
             ['Full Stack Ninjas']),
            # Reliability_Tool
            ('Reliability_Tool', 'The Lambda Legends', 'Layla Russell',
             'Serverless architecture, event-driven development and microservice automation.',
             '#reliability-lambda-legends', 'https://is.gd/MTQ974X',
             'Serverless Computing,AWS Lambda,Node.js,Python',
             ['API Avengers']),
            ('Reliability_Tool', 'The Encryption Squad', 'Ethan Griffin',
             'Cybersecurity research, cryptographic key management and secure data storage.',
             '#reliability-encryption-squad', 'https://short.io/T9X47QM',
             'Cryptography (AES/RSA/SHA-256),Security Audits',
             ['API Avengers', 'The API Explorers']),
            ('Reliability_Tool', 'The UX Wizards', 'Aurora Cooper',
             'Accessibility, user behaviour analytics and UI/UX best practices.',
             '#reliability-ux-wizards', 'https://tiny.cc/Q7MTX94',
             'UI/UX Design,Figma,Adobe XD,Usability Testing',
             ['Full Stack Ninjas', 'The Feature Crafters']),
            ('Reliability_Tool', 'The Hackathon Hustlers', 'Dylan Spencer',
             'Rapid prototyping, proof-of-concept development and hackathon facilitation.',
             '#reliability-hackathon-hustlers', 'https://bit.ly/MT7XQ49',
             'Rapid Prototyping,MVP Development,No-Code Tools',
             ['The UX Wizards']),
            ('Reliability_Tool', 'The Frontend Phantoms', 'Stella Martinez',
             'Frontend frameworks, web performance tuning and component libraries.',
             '#reliability-frontend-phantoms', 'https://t.ly/9T7QX4M',
             'React,Vue,Angular,Performance Optimisation',
             ['The API Explorers']),
            # Arch
            ('Arch', 'The Dev Dragons', 'Levi Bishop',
             'API integrations, SDK development and plugin architecture.',
             '#arch-dev-dragons', 'https://goo.gl/QXMT974',
             'API Development,SDK Development,Plugin Architecture',
             ['The Feature Crafters']),
            ('Arch', 'The Microservice Mavericks', 'Eleanor Freeman',
             'Microservice governance, inter-service communication and API gateways.',
             '#arch-microservice-mavericks', 'https://tinyurl.com/7T9QMX4',
             'Service Mesh (Istio/Envoy),API Gateway,gRPC',
             ['The Code Refactors', 'The Lambda Legends']),
            # Programme
            ('Programme', 'The Quantum Coders', 'Hudson Ford',
             'Quantum computing simulations, parallel processing and AI-assisted coding.',
             '#programme-quantum-coders', 'https://bit.do/X9T7Q4M',
             'Quantum Computing,Qiskit,Parallel Computing',
             ['Kernel Crushers']),
        ]

        # Create teams
        teams = {}
        pool = MEMBERS_POOL
        for idx, (dept_key, tname, manager, purpose, channel, github, skills_csv, _downstream) in enumerate(teams_raw):
            dept = depts.get(dept_key)
            if not dept:
                continue
            mgr_email = email_from_name(manager)
            team, created = Team.objects.get_or_create(
                name=tname,
                defaults=dict(
                    department=dept,
                    manager_name=manager,
                    manager_email=mgr_email,
                    purpose=purpose,
                    contact_channel=channel,
                    github_url=github,
                )
            )
            if not created:
                team.department = dept
                team.manager_name = manager
                team.manager_email = mgr_email
                team.purpose = purpose
                team.contact_channel = channel
                team.github_url = github
                team.save()

            team.skills.clear()
            for skill_name in skills_csv.split(','):
                skill_name = skill_name.strip()
                if skill_name:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    team.skills.add(skill)

            # Assign 5-7 members rotating through pool
            team.members.all().delete()
            start = (idx * 5) % len(pool)
            member_slice = [pool[(start + i) % len(pool)] for i in range(6)]
            assign_members(team, member_slice)

            teams[tname] = team
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} team: {tname}')

        # Set upstream dependencies
        for _dept, tname, _mgr, _p, _c, _g, _s, downstream_names in teams_raw:
            team = teams.get(tname)
            if not team:
                continue
            for downstream_name in downstream_names:
                downstream_team = teams.get(downstream_name)
                if downstream_team:
                    # This team is upstream of downstream_team
                    downstream_team.upstream_dependencies.add(team)

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete: {len(depts)} departments, {len(teams)} teams, '
            f'{TeamMember.objects.count()} members.'
        ))
