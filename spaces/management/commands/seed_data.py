import os, urllib.request, tempfile, random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.db import transaction

from accounts.models import UserProfile
from spaces.models import (
    Space, SpaceImage, SpaceAmenity, AdditionalService,
    SpaceType, City, RentalType,
)
from reviews.models import Review


PHOTO_IDS = {
    'office':    ['1170', '260',  '1216'],
    'hall':      ['169',  '159',  '1181'],
    'studio':    ['20',   '96',   '355'],
    'coworking': ['380',  '3184', '1080'],
    'meeting':   ['706',  '587',  '1080'],
    'event':     ['265',  '169',  '450'],
}


def download_photo(photo_id, width=900, height=600):
    url = f'https://picsum.photos/id/{photo_id}/{width}/{height}'
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            tmp.write(resp.read())
        tmp.flush()
        return tmp.name
    except Exception:
        tmp.close()
        return None


cities_data = {
    'riyadh': {
        'lat': '24.68', 'lng': '46.69',
        'ar': 'الرياض',
        'areas': ['حي العليا', 'حي السليمانية', 'حي الملقا', 'حي النرجس', 'حي الروضة',
                  'حي الورود', 'حي الغدير', 'حي الربوة', 'حي المروج', 'حي الياسمين'],
    },
    'jeddah': {
        'lat': '21.52', 'lng': '39.17',
        'ar': 'جدة',
        'areas': ['حي الحمراء', 'كورنيش جدة', 'حي الروضة', 'حي الزهراء', 'حي النزهة',
                  'حي السلامة', 'حي الفيصلية', 'حي البوادي', 'حي مشرفة', 'حي الصفا'],
    },
    'dammam': {
        'lat': '26.43', 'lng': '50.10',
        'ar': 'الدمام',
        'areas': ['حي الشاطئ', 'حي الفيصلية', 'حي العنود', 'حي المزروعية', 'حي الأمانة',
                  'حي الإسكان', 'حي النور', 'حي الخليج', 'حي الروضة', 'حي القادسية'],
    },
    'makkah': {
        'lat': '21.42', 'lng': '39.82',
        'ar': 'مكة المكرمة',
        'areas': ['حي العزيزية', 'حي النسيم', 'حي الشوقية', 'حي الرصيفة', 'حي الزاهر',
                  'حي أجياد', 'حي المسفلة', 'حي الهجرة', 'حي الششة', 'حي الجوهرة'],
    },
    'madinah': {
        'lat': '24.47', 'lng': '39.61',
        'ar': 'المدينة المنورة',
        'areas': ['حي العزيزية', 'حي قباء', 'حي الحرة الغربية', 'حي الدفاع', 'حي السلام',
                  'حي المطار', 'حي الإسكان', 'حي الخالدية', 'حي الملك فهد', 'حي النخيل'],
    },
}

space_types_rotation = [
    ('office',    'مكتب تنفيذي',    PHOTO_IDS['office'],    ['wifi', 'ac', 'coffee', 'parking'],               500,  8000,  10),
    ('meeting',   'قاعة اجتماعات',  PHOTO_IDS['meeting'],   ['wifi', 'screen', 'ac', 'projector'],             800,  12000, 15),
    ('studio',    'استوديو إبداعي', PHOTO_IDS['studio'],    ['wifi', 'ac', 'coffee'],                          1000, 15000, 12),
    ('coworking', 'مساحة مشتركة',   PHOTO_IDS['coworking'], ['wifi', 'coffee', 'ac', 'printer', 'parking'],    200,  3000,  8),
    ('hall',      'قاعة كبيرة',     PHOTO_IDS['hall'],      ['wifi', 'screen', 'ac', 'parking', 'security'],   3000, 40000, 20),
    ('training',  'غرفة تدريب',     PHOTO_IDS['event'],     ['wifi', 'screen', 'whiteboard', 'ac', 'coffee'],  1200, 18000, 15),
    ('event',     'مساحة فعاليات',  PHOTO_IDS['event'],     ['wifi', 'ac', 'parking', 'security'],             2500, 35000, 18),
    ('office',    'مكتب مرن',       PHOTO_IDS['office'],    ['wifi', 'ac', 'coffee'],                          300,  5000,  8),
    ('meeting',   'غرفة مناقشة',    PHOTO_IDS['meeting'],   ['wifi', 'screen', 'ac'],                          600,  9000,  10),
    ('coworking', 'ديسك مشترك',     PHOTO_IDS['coworking'], ['wifi', 'coffee', 'printer'],                     150,  2500,  6),
]

REVIEWS_POOL = [
    {'rating': 5, 'cleanliness': 5, 'internet': 5, 'parking_rate': 5, 'quietness': 5, 'host_service': 5,
     'comment': 'مساحة رائعة جداً! تجاوزت توقعاتنا في كل شيء. سنعود بالتأكيد.'},
    {'rating': 5, 'cleanliness': 5, 'internet': 4, 'parking_rate': 5, 'quietness': 4, 'host_service': 5,
     'comment': 'تجربة ممتازة من البداية للنهاية. المساحة نظيفة والخدمة احترافية.'},
    {'rating': 4, 'cleanliness': 4, 'internet': 5, 'parking_rate': 3, 'quietness': 4, 'host_service': 5,
     'comment': 'مكان جيد جداً وموقع ممتاز. الإنترنت كانت سريعة جداً.'},
    {'rating': 4, 'cleanliness': 5, 'internet': 4, 'parking_rate': 4, 'quietness': 5, 'host_service': 4,
     'comment': 'هادئ ومريح للعمل. الإضاءة الطبيعية رائعة.'},
    {'rating': 5, 'cleanliness': 5, 'internet': 5, 'parking_rate': 5, 'quietness': 5, 'host_service': 5,
     'comment': 'الأفضل في المنطقة! فريق العمل محترف للغاية.'},
    {'rating': 3, 'cleanliness': 3, 'internet': 4, 'parking_rate': 3, 'quietness': 3, 'host_service': 4,
     'comment': 'مقبول بشكل عام، يحتاج بعض التحسينات.'},
]


class Command(BaseCommand):
    help = 'Seed database - 10 spaces per city'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help='Clear existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing...')
            Review.objects.all().delete()
            SpaceImage.objects.all().delete()
            SpaceAmenity.objects.all().delete()
            AdditionalService.objects.all().delete()
            Space.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Cleared.'))

        with transaction.atomic():
            owners  = self._create_owners()
            tenants = self._create_tenants()
            self._create_spaces(owners, tenants)

        self.stdout.write(self.style.SUCCESS(
            '\n✅ تم إضافة 50 مساحة (10 لكل مدينة)!\n'
            '   تسجيل دخول: tenant1 / pass1234\n'
        ))

    def _create_owners(self):
        owners = []
        for uname, first, last, email, phone in [
            ('owner_ahmed', 'Ahmed', 'Al-Rashidi', 'ahmed@spacehub.sa', '0501234567'),
            ('owner_sara',  'Sara',  'Al-Qahtani', 'sara@spacehub.sa',  '0559876543'),
        ]:
            u, created = User.objects.get_or_create(username=uname, defaults={
                'first_name': first, 'last_name': last, 'email': email,
            })
            if created:
                u.set_password('pass1234')
                u.save()
            prof, _ = UserProfile.objects.get_or_create(user=u, defaults={'role': 'owner', 'phone': phone})
            prof.role = 'owner'
            prof.save()
            owners.append(u)
            self.stdout.write(f'Owner: {uname}')
        return owners

    def _create_tenants(self):
        tenants = []
        for uname, first, last, email, phone in [
            ('tenant1', 'محمد', 'العتيبي',  'tenant1@mail.com', '0551112222'),
            ('tenant2', 'نورة', 'السعدي',   'tenant2@mail.com', '0553334444'),
            ('tenant3', 'خالد', 'الزهراني', 'tenant3@mail.com', '0555556666'),
        ]:
            u, created = User.objects.get_or_create(username=uname, defaults={
                'first_name': first, 'last_name': last, 'email': email,
            })
            if created:
                u.set_password('pass1234')
                u.save()
            prof, _ = UserProfile.objects.get_or_create(user=u, defaults={'role': 'tenant', 'phone': phone})
            prof.role = 'tenant'
            prof.save()
            tenants.append(u)
            self.stdout.write(f'Tenant: {uname}')
        return tenants

    def _create_spaces(self, owners, tenants):
        owner_idx = 0
        for city_code, city_info in cities_data.items():
            self.stdout.write(f'\n── {city_info["ar"]} ──')
            for i in range(10):
                stype, stype_ar, photos, amenities, price_day, price_month, capacity = space_types_rotation[i]
                area  = city_info['areas'][i]
                owner = owners[owner_idx % len(owners)]
                owner_idx += 1

                title = f'{stype_ar} - {area} - {city_info["ar"]}'
                self.stdout.write(f'  {title}')

                maps_url = f'https://maps.google.com/maps?q={city_info["lat"]},{city_info["lng"]}&z=15&output=embed'

                space, created = Space.objects.get_or_create(
                    title=title,
                    defaults=dict(
                        owner=owner,
                        description=f'مساحة {stype_ar} احترافية في {area} بمدينة {city_info["ar"]}. مجهزة بالكامل وتوفر بيئة عمل مريحة وإنتاجية.',
                        space_type=stype,
                        city=city_code,
                        address=f'{area}، {city_info["ar"]}',
                        price_per_day=price_day,
                        price_monthly=price_month,
                        capacity=capacity,
                        area_sqm=capacity * 5,
                        rental_type='daily',
                        allow_dynamic_pricing=i % 3 == 0,
                        discount_pct=10 if i % 3 == 0 else 0,
                        maps_embed_url=maps_url,
                        status='available',
                    )
                )

                if not created:
                    self.stdout.write('  already exists')
                    continue

                self._add_photos(space, photos)

                for amenity_name in amenities:
                    SpaceAmenity.objects.get_or_create(space=space, name=amenity_name)

                if stype in ('hall', 'event'):
                    AdditionalService.objects.get_or_create(
                        space=space, service_type='catering',
                        defaults={'price': 500, 'description': 'خدمة ضيافة متكاملة'}
                    )

                self._add_reviews(space, tenants)
                self.stdout.write(self.style.SUCCESS('  ✓'))

    def _add_photos(self, space, photo_ids):
        media_path = 'media/spaces/'

        # local img
        if os.path.exists(media_path):
            all_images = [f for f in os.listdir(media_path)
                         if f.lower().endswith(('.jpeg', '.jpg', '.png'))]
        else:
            all_images = []

        if all_images:
            # two random photo 
            selected = random.sample(all_images, min(2, len(all_images)))
            is_main = True
            for img_name in selected:
                SpaceImage.objects.create(
                    space=space,
                    image=f'spaces/{img_name}',
                    is_main=is_main
                )
                is_main = False
            self.stdout.write(f'  📷 {len(selected)} local photos')
        else:
            # fallback int
            is_main = True
            for idx, pid in enumerate(photo_ids[:2]):
                tmp_path = download_photo(pid)
                if tmp_path:
                    with open(tmp_path, 'rb') as f:
                        img_obj = SpaceImage(space=space, is_main=is_main)
                        img_obj.image.save(f'space_{space.pk}_{idx}.jpg', File(f), save=True)
                    os.unlink(tmp_path)
                is_main = False

    def _add_reviews(self, space, tenants):
        num = random.randint(2, min(len(tenants), len(REVIEWS_POOL)))
        for tenant, rv in zip(random.sample(tenants, num), random.sample(REVIEWS_POOL, num)):
            Review.objects.get_or_create(
                space=space, user=tenant,
                defaults={
                    'rating':       rv['rating'],
                    'comment':      rv['comment'],
                    'cleanliness':  rv['cleanliness'],
                    'internet':     rv['internet'],
                    'parking_rate': rv['parking_rate'],
                    'quietness':    rv['quietness'],
                    'host_service': rv['host_service'],
                }
            )