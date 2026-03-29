"""
Management command to seed the database with sample data for development/demo.
Seeds: Practice Areas, Lawyers, Blog Categories, Blog Posts, Cases.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with sample lawyers, blog posts, practice areas, and cases'

    def handle(self, *args, **options):
        self.seed_practice_areas()
        self.seed_lawyers()
        self.seed_blog_categories_and_tags()
        self.seed_blog_posts()
        self.seed_cases()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def seed_practice_areas(self):
        from lawyers.models import PracticeArea

        areas = [
            {
                'name': 'Criminal Law',
                'description': 'Defense and prosecution in criminal cases',
                'icon_name': 'gavel',
                'detailed_description': 'Criminal law involves prosecution by the government of a person for an act that has been classified as a crime. It includes offenses like theft, assault, robbery, murder, and more.',
            },
            {
                'name': 'Family Law',
                'description': 'Divorce, custody, and family disputes',
                'icon_name': 'family_restroom',
                'detailed_description': 'Family law deals with family-related issues and domestic relations including marriage, divorce, child custody, adoption, and domestic violence cases.',
            },
            {
                'name': 'Civil Law',
                'description': 'Property disputes, contracts, and civil rights',
                'icon_name': 'balance',
                'detailed_description': 'Civil law covers disputes between individuals or organizations, including property disputes, contract breaches, tort claims, and other non-criminal legal matters.',
            },
            {
                'name': 'Corporate Law',
                'description': 'Business formation, compliance, and corporate governance',
                'icon_name': 'business',
                'detailed_description': 'Corporate law governs the formation and operations of corporations, including mergers, acquisitions, corporate governance, and regulatory compliance.',
            },
            {
                'name': 'Property Law',
                'description': 'Real estate transactions and property disputes',
                'icon_name': 'home',
                'detailed_description': 'Property law involves the various forms of ownership and tenancy in real property and personal property, including land transactions, tenant rights, and boundary disputes.',
            },
        ]

        for area_data in areas:
            obj, created = PracticeArea.objects.get_or_create(
                name=area_data['name'],
                defaults=area_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Practice Area: {obj.name} - {status}')

    def seed_lawyers(self):
        from accounts.models import User
        from lawyers.models import LawyerProfile, PracticeArea

        lawyers_data = [
            {
                'email': 'rahim@example.com',
                'first_name': 'Rahim',
                'last_name': 'Uddin',
                'phone': '+8801711111111',
                'profile': {
                    'profession': 'Advocate',
                    'specialization': 'Criminal Defense',
                    'bio': 'Senior criminal lawyer with over 12 years of experience in the Dhaka courts. Specializes in criminal defense and has successfully represented hundreds of clients.',
                    'years_experience': 12,
                    'solved_cases': 120,
                    'consultancy_fees': Decimal('5000.00'),
                    'rating': Decimal('4.70'),
                    'is_available': True,
                    'gender': 'male',
                },
                'practice_areas': ['Criminal Law', 'Civil Law'],
            },
            {
                'email': 'fatema@example.com',
                'first_name': 'Fatema',
                'last_name': 'Begum',
                'phone': '+8801722222222',
                'profile': {
                    'profession': 'Barrister',
                    'specialization': 'Family Law',
                    'bio': 'Experienced family law practitioner dedicated to resolving domestic disputes, custody battles, and divorce proceedings with compassion and expertise.',
                    'years_experience': 8,
                    'solved_cases': 85,
                    'consultancy_fees': Decimal('4000.00'),
                    'rating': Decimal('4.50'),
                    'is_available': True,
                    'gender': 'female',
                },
                'practice_areas': ['Family Law', 'Civil Law'],
            },
            {
                'email': 'karim@example.com',
                'first_name': 'Karim',
                'last_name': 'Ahmed',
                'phone': '+8801733333333',
                'profile': {
                    'profession': 'Senior Advocate',
                    'specialization': 'Corporate Law',
                    'bio': 'Leading corporate law expert specializing in business formation, mergers & acquisitions, and regulatory compliance for both local and international firms.',
                    'years_experience': 15,
                    'solved_cases': 200,
                    'consultancy_fees': Decimal('8000.00'),
                    'rating': Decimal('4.90'),
                    'is_available': True,
                    'gender': 'male',
                },
                'practice_areas': ['Corporate Law', 'Property Law'],
            },
            {
                'email': 'naima@example.com',
                'first_name': 'Naima',
                'last_name': 'Sultana',
                'phone': '+8801744444444',
                'profile': {
                    'profession': 'Advocate',
                    'specialization': 'Property Law',
                    'bio': 'Property law specialist handling land disputes, real estate transactions, and boundary conflicts. Known for meticulous documentation and strong court representation.',
                    'years_experience': 10,
                    'solved_cases': 95,
                    'consultancy_fees': Decimal('4500.00'),
                    'rating': Decimal('4.60'),
                    'is_available': True,
                    'gender': 'female',
                },
                'practice_areas': ['Property Law', 'Civil Law'],
            },
            {
                'email': 'hassan@example.com',
                'first_name': 'Hassan',
                'last_name': 'Ali',
                'phone': '+8801755555555',
                'profile': {
                    'profession': 'Barrister',
                    'specialization': 'Criminal and Civil Law',
                    'bio': 'Versatile legal professional with extensive experience in both criminal and civil matters. Committed to justice and fair representation for all clients.',
                    'years_experience': 7,
                    'solved_cases': 60,
                    'consultancy_fees': Decimal('3500.00'),
                    'rating': Decimal('4.30'),
                    'is_available': True,
                    'gender': 'male',
                },
                'practice_areas': ['Criminal Law', 'Family Law'],
            },
        ]

        for lawyer_data in lawyers_data:
            user, created = User.objects.get_or_create(
                email=lawyer_data['email'],
                defaults={
                    'first_name': lawyer_data['first_name'],
                    'last_name': lawyer_data['last_name'],
                    'phone': lawyer_data['phone'],
                    'role': User.Role.LAWYER,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('lawyer123')
                user.save()

            profile_data = lawyer_data['profile']
            profile, _ = LawyerProfile.objects.get_or_create(
                user=user,
                defaults=profile_data
            )
            if not _:
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()

            # Set practice areas
            pa_names = lawyer_data['practice_areas']
            areas = PracticeArea.objects.filter(name__in=pa_names)
            profile.practice_areas.set(areas)

            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  Lawyer: {user.full_name} - {status}')

    def seed_blog_categories_and_tags(self):
        from blog.models import Category, Tag

        categories = [
            {'name': 'Legal Tips', 'description': 'Helpful legal tips for everyday life'},
            {'name': 'Case Studies', 'description': 'Detailed analysis of notable legal cases'},
            {'name': 'Law Updates', 'description': 'Latest updates in Bangladesh law and judiciary'},
        ]

        for cat_data in categories:
            obj, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Category: {obj.name} - {status}')

        tags = ['criminal', 'law', 'property', 'family', 'corporate', 'rights', 'court', 'bangladesh', 'legal-advice']
        for tag_name in tags:
            obj, created = Tag.objects.get_or_create(name=tag_name)
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Tag: {obj.name} - {status}')

    def seed_blog_posts(self):
        from accounts.models import User
        from blog.models import BlogPost, Category, Tag

        # Get or create an admin user for blog authorship
        admin_user, created = User.objects.get_or_create(
            email='admin@thechamberone.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        now = timezone.now()
        posts_data = [
            {
                'title': 'Understanding Criminal Law in Bangladesh',
                'content': '''<h2>Introduction to Criminal Law</h2>
<p>Criminal law in Bangladesh is primarily governed by the Penal Code of 1860 and the Code of Criminal Procedure of 1898. These laws define various criminal offenses and prescribe punishments for them.</p>
<h2>Key Principles</h2>
<p>The fundamental principles of criminal law in Bangladesh include the presumption of innocence, the right to a fair trial, and the right to legal representation. Every accused person has the right to be defended by a lawyer of their choice.</p>
<h2>Common Criminal Offenses</h2>
<p>Common criminal offenses in Bangladesh include theft, robbery, assault, murder, fraud, and cybercrime. Each offense carries specific penalties ranging from fines to imprisonment.</p>
<h2>The Court System</h2>
<p>Criminal cases in Bangladesh are heard by Magistrate Courts, Sessions Courts, and the High Court Division. The Supreme Court serves as the highest appellate authority.</p>''',
                'excerpt': 'A comprehensive guide to understanding criminal law in Bangladesh, including key principles, common offenses, and the court system.',
                'category_name': 'Legal Tips',
                'tag_names': ['criminal', 'law', 'bangladesh'],
                'published_date': now - timedelta(days=14),
                'views_count': 150,
                'is_featured': True,
            },
            {
                'title': 'Property Rights and Land Disputes: A Complete Guide',
                'content': '''<h2>Property Rights in Bangladesh</h2>
<p>Property rights in Bangladesh are governed by various laws including the Transfer of Property Act 1882, the Registration Act 1908, and the Land Management Manual. Understanding these laws is crucial for anyone involved in property transactions.</p>
<h2>Common Land Disputes</h2>
<p>Land disputes in Bangladesh often involve boundary conflicts, inheritance claims, fraudulent transfers, and encroachment. These disputes can be complex and may require extensive documentation to resolve.</p>
<h2>How to Protect Your Property</h2>
<p>To protect your property rights, always ensure proper documentation, register all property transactions, maintain updated land records, and consult a qualified property lawyer for any transactions.</p>
<h2>Legal Remedies</h2>
<p>If you face a property dispute, legal remedies include filing a civil suit, seeking injunctions, and pursuing alternative dispute resolution methods like mediation and arbitration.</p>''',
                'excerpt': 'Everything you need to know about property rights and land disputes in Bangladesh, including legal remedies and protection strategies.',
                'category_name': 'Legal Tips',
                'tag_names': ['property', 'rights', 'legal-advice'],
                'published_date': now - timedelta(days=10),
                'views_count': 98,
                'is_featured': False,
            },
            {
                'title': 'Family Law: Navigating Divorce and Custody in Bangladesh',
                'content': '''<h2>Family Law Overview</h2>
<p>Family law in Bangladesh addresses matters related to marriage, divorce, child custody, maintenance, and inheritance. The laws differ based on religious personal laws — Muslim Family Laws Ordinance 1961, Hindu Marriage Act, and Christian Marriage Act.</p>
<h2>Divorce Proceedings</h2>
<p>Divorce in Bangladesh can be initiated by either spouse. Under Muslim law, the husband can pronounce talaq, while the wife can seek divorce through khula or judicial decree. The process involves notice periods and attempts at reconciliation.</p>
<h2>Child Custody</h2>
<p>Child custody decisions are made based on the best interests of the child. Generally, mothers have custody rights for young children, while fathers retain guardianship. Courts consider factors like the child's age, welfare, and the parents' ability to provide care.</p>
<h2>Seeking Legal Help</h2>
<p>Family disputes can be emotionally challenging. It is advisable to seek the help of an experienced family law attorney who can guide you through the legal process with sensitivity and expertise.</p>''',
                'excerpt': 'A guide to family law in Bangladesh covering divorce proceedings, child custody, and how to navigate these sensitive legal matters.',
                'category_name': 'Case Studies',
                'tag_names': ['family', 'law', 'court'],
                'published_date': now - timedelta(days=7),
                'views_count': 75,
                'is_featured': True,
            },
            {
                'title': 'Corporate Law Essentials for Business Owners',
                'content': '''<h2>Starting a Business in Bangladesh</h2>
<p>Setting up a business in Bangladesh requires compliance with the Companies Act 1994, the Partnership Act 1932, and various regulatory requirements. Understanding these legal frameworks is essential for entrepreneurs.</p>
<h2>Company Registration</h2>
<p>To register a company, you need to submit the Memorandum and Articles of Association to the Registrar of Joint Stock Companies and Firms (RJSC). The process includes name clearance, document submission, and obtaining a certificate of incorporation.</p>
<h2>Corporate Governance</h2>
<p>Good corporate governance ensures transparency, accountability, and fair management of a company. It includes proper board meetings, financial reporting, and compliance with the Bangladesh Securities and Exchange Commission (BSEC) regulations.</p>
<h2>Tax Obligations</h2>
<p>Businesses must comply with the Income Tax Ordinance 1984 and the Value Added Tax Act 2012. Proper tax planning and compliance are crucial for sustainable business operations.</p>''',
                'excerpt': 'Essential corporate law knowledge for business owners in Bangladesh, covering registration, governance, and tax obligations.',
                'category_name': 'Law Updates',
                'tag_names': ['corporate', 'law', 'bangladesh'],
                'published_date': now - timedelta(days=3),
                'views_count': 42,
                'is_featured': False,
            },
            {
                'title': 'Your Rights When Arrested: What Every Citizen Should Know',
                'content': '''<h2>Fundamental Rights During Arrest</h2>
<p>Under the Constitution of Bangladesh, every citizen has fundamental rights that must be respected during an arrest. Article 33 guarantees the right to be informed of the grounds of arrest, the right to consult and be defended by a lawyer, and the right to be produced before a magistrate within 24 hours.</p>
<h2>What to Do If You Are Arrested</h2>
<p>If you are arrested, remain calm and do not resist. Ask for the reason for your arrest. Request to speak to a lawyer immediately. Do not sign any document without legal counsel. You have the right to inform a family member about your arrest.</p>
<h2>Bail Provisions</h2>
<p>Bail is a right in bailable offenses and can be granted by the court in non-bailable offenses. Your lawyer can file a bail petition in the appropriate court to secure your release.</p>
<h2>Filing Complaints Against Unlawful Arrest</h2>
<p>If you believe your arrest was unlawful, you can file a writ petition in the High Court Division under Article 102 of the Constitution, or lodge a complaint with the police commission.</p>''',
                'excerpt': 'Know your legal rights during an arrest in Bangladesh — from the right to a lawyer to bail provisions and filing complaints.',
                'category_name': 'Legal Tips',
                'tag_names': ['criminal', 'rights', 'legal-advice'],
                'published_date': now - timedelta(days=1),
                'views_count': 210,
                'is_featured': True,
            },
        ]

        for post_data in posts_data:
            category = Category.objects.filter(name=post_data['category_name']).first()
            post, created = BlogPost.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'content': post_data['content'],
                    'excerpt': post_data['excerpt'],
                    'author': admin_user,
                    'category': category,
                    'status': BlogPost.Status.PUBLISHED,
                    'published_date': post_data['published_date'],
                    'views_count': post_data['views_count'],
                    'is_featured': post_data['is_featured'],
                }
            )
            if created:
                tags = Tag.objects.filter(name__in=post_data['tag_names'])
                post.tags.set(tags)
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Blog Post: {post.title[:50]} - {status}')

    def seed_cases(self):
        from accounts.models import User
        from cases.models import Case, CaseTimeline
        from lawyers.models import LawyerProfile, PracticeArea

        # Get a client user (create if needed)
        client_user, created = User.objects.get_or_create(
            email='client@example.com',
            defaults={
                'first_name': 'Aminul',
                'last_name': 'Khan',
                'phone': '+8801766666666',
                'role': User.Role.CLIENT,
                'is_active': True,
            }
        )
        if created:
            client_user.set_password('client123')
            client_user.save()

        client_user2, created = User.objects.get_or_create(
            email='client2@example.com',
            defaults={
                'first_name': 'Roksana',
                'last_name': 'Akter',
                'phone': '+8801777777777',
                'role': User.Role.CLIENT,
                'is_active': True,
            }
        )
        if created:
            client_user2.set_password('client123')
            client_user2.save()

        lawyers = LawyerProfile.objects.all()
        if not lawyers.exists():
            self.stdout.write(self.style.WARNING('  No lawyers found, skipping case seeding'))
            return

        now = timezone.now()
        cases_data = [
            {
                'title': 'Property Dispute - Khan vs Ahmed',
                'case_number': 'CS-2026-001',
                'description': 'Property boundary dispute in Dhaka involving contested land ownership between two neighboring families.',
                'court_name': 'Dhaka Judge Court',
                'client': client_user,
                'lawyer_email': 'naima@example.com',
                'practice_area': 'Property Law',
                'status': Case.Status.OPEN,
                'next_hearing_date': now + timedelta(days=12),
                'filing_date': (now - timedelta(days=28)).date(),
                'timeline': [
                    {'date': (now - timedelta(days=28)).date(), 'event': 'Case Filed', 'description': 'Initial filing of the property dispute case'},
                    {'date': (now - timedelta(days=14)).date(), 'event': 'First Hearing', 'description': 'Both parties presented initial arguments'},
                ],
            },
            {
                'title': 'Criminal Appeal - State vs Hasan',
                'case_number': 'CR-2026-015',
                'description': 'Criminal appeal against conviction. The defendant seeks to overturn the lower court verdict on grounds of insufficient evidence.',
                'court_name': 'High Court Division, Dhaka',
                'client': client_user,
                'lawyer_email': 'rahim@example.com',
                'practice_area': 'Criminal Law',
                'status': Case.Status.IN_PROGRESS,
                'next_hearing_date': now + timedelta(days=20),
                'filing_date': (now - timedelta(days=60)).date(),
                'timeline': [
                    {'date': (now - timedelta(days=60)).date(), 'event': 'Appeal Filed', 'description': 'Appeal petition submitted to High Court'},
                    {'date': (now - timedelta(days=45)).date(), 'event': 'Hearing Scheduled', 'description': 'Court accepted the appeal and scheduled hearing'},
                    {'date': (now - timedelta(days=30)).date(), 'event': 'Evidence Reviewed', 'description': 'Judge reviewed additional evidence submitted by defense'},
                ],
            },
            {
                'title': 'Divorce Settlement - Akter vs Akter',
                'case_number': 'FM-2026-008',
                'description': 'Divorce case involving custody dispute and asset division between the parties.',
                'court_name': 'Family Court, Dhaka',
                'client': client_user2,
                'lawyer_email': 'fatema@example.com',
                'practice_area': 'Family Law',
                'status': Case.Status.PENDING,
                'next_hearing_date': now + timedelta(days=5),
                'filing_date': (now - timedelta(days=40)).date(),
                'timeline': [
                    {'date': (now - timedelta(days=40)).date(), 'event': 'Case Filed', 'description': 'Divorce petition filed in Family Court'},
                    {'date': (now - timedelta(days=20)).date(), 'event': 'Mediation Attempted', 'description': 'Court-ordered mediation session conducted'},
                ],
            },
        ]

        for case_data in cases_data:
            lawyer = None
            try:
                lawyer = LawyerProfile.objects.get(user__email=case_data['lawyer_email'])
            except LawyerProfile.DoesNotExist:
                lawyer = lawyers.first()

            practice_area = PracticeArea.objects.filter(name=case_data['practice_area']).first()

            case, created = Case.objects.get_or_create(
                case_number=case_data['case_number'],
                defaults={
                    'title': case_data['title'],
                    'description': case_data['description'],
                    'court_name': case_data['court_name'],
                    'client': case_data['client'],
                    'lawyer': lawyer,
                    'practice_area': practice_area,
                    'status': case_data['status'],
                    'next_hearing_date': case_data['next_hearing_date'],
                    'filing_date': case_data['filing_date'],
                }
            )

            if created:
                admin_user = User.objects.filter(is_staff=True).first()
                for tl in case_data['timeline']:
                    CaseTimeline.objects.create(
                        case=case,
                        date=tl['date'],
                        event=tl['event'],
                        description=tl['description'],
                        created_by=admin_user or case_data['client'],
                    )

            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Case: {case.title} - {status}')
