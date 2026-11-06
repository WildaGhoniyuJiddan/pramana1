"""
scripts/corpus_translations_data.py

Curated English translations for all 42 chunks and 29 registry documents in Pramana corpus.
All translations follow strict rules:
1. Literal and faithful statutory phrasing.
2. 100% numerical, article reference ('Pasal N'), and currency ('Rp N') parity with Indonesian verbatim source.
3. Cultural glosses according to corpus/glossary.json.
4. Unique descriptive title_en for every chunk.
"""

TRANSLATIONS_DOCUMENTS = {   'awig-awig-desa-adat-penglipuran': 'Customary Village Bylaws (Awig-awig) of Penglipuran Customary Village, Bangli '
                                       'Regency',
    'awig-awig-desa-adat-tenganan-pegringsingan': 'Customary Village Bylaws (Awig-awig) of Tenganan Pegringsingan '
                                                  'Customary Village, Karangasem Regency',
    'awig-awig-penglipuran': 'Customary Village Bylaws (Awig-awig) of Penglipuran Village',
    'awig-awig-tenganan': 'Customary Village Bylaws (Awig-awig) of Tenganan Pegringsingan Village',
    'kepgub-bali-699-2025': 'Bali Governor Decree No. 699/2025 on Cultural Tourism Area Boundaries',
    'perda-bali-2-2023': 'Bali Provincial Regional Regulation No. 2/2023 on Traditional Balinese Architectural '
                         'Heritage',
    'perda-bali-2-2025': 'Bali Provincial Regional Regulation No. 2/2025 on Amendments to Regional Regulation No. '
                         '6/2023 on Foreign Tourist Levy',
    'perda-bali-4-2019': 'Bali Provincial Regional Regulation No. 4/2019 on Customary Villages (Desa Adat) in Bali',
    'perda-bali-5-2020': 'Bali Provincial Regional Regulation No. 5/2020 on Standards for the Implementation of '
                         'Balinese Cultural Tourism',
    'perda-bali-6-2023': 'Bali Provincial Regional Regulation No. 6/2023 on Foreign Tourist Levy for Protection of '
                         'Culture and Natural Environment',
    'pergub-bali-2-2024': 'Bali Governor Regulation No. 2/2024 on Procedures for Foreign Tourist Levy Payment',
    'pergub-bali-25-2020': 'Bali Governor Regulation No. 25/2020 on Facilitation of Sacred Temple Protection',
    'pergub-bali-25-2025': 'Bali Governor Regulation No. 25/2025 on Amendments to Governor Regulation No. 2/2024 on '
                           'Foreign Tourist Levy Procedures',
    'pergub-bali-36-2023': 'Bali Governor Regulation No. 36/2023 on Tourism Governance Guidelines',
    'pergub-bali-4-2020': 'Bali Governor Regulation No. 4/2020 on Customary Village Enforcement Coordination',
    'pergub-bali-52-2021': 'Bali Governor Regulation No. 52/2021 on Public Order and Community Tranquility',
    'se-gubernur-bali-4-2023': 'Bali Governor Circular Letter No. 4/2023 on New Standards for Foreign Tourists in Bali '
                               "(Do's & Don'ts)",
    'se-gubernur-bali-7-2025': 'Bali Governor Circular Letter No. 7/2025 on Refinement of Foreign Tourist Standards',
    'se-kapolri-6-2015': 'Chief of Indonesian National Police Circular Letter No. 6/2015 on Hate Speech Handling',
    'seruan-bersama-nyepi-2025': 'Joint Decree of PHDI and Bali Customary Village Council (MDA) on Guidelines for '
                                 'Nyepi Day Observance',
    'seruan-bersama-nyepi-2026': 'Joint Decree of Religious and Customary Councils on the Observance of the Nyepi Holy '
                                 'Day, Saka New Year 1948 / 2026 CE (Coinciding with Idul Fitri Takbiran Night 1447 H '
                                 '/ 2026 CE)',
    'skb-ite-2021': 'Joint Ministerial Decree on Guidelines for Implementation of the Electronic Information and '
                    'Transactions Law (ITE)',
    'uu-1-2023': 'Law of the Republic of Indonesia No. 1/2023 on the Criminal Code (KUHP)',
    'uu-1-2024': 'Second Amendment to Law No. 11/2008 on Electronic Information and Transactions (ITE Law)',
    'uu-11-2010': 'Law of the Republic of Indonesia No. 11/2010 on Cultural Heritage',
    'uu-15-2023': 'Law of the Republic of Indonesia No. 15/2023 on Bali Province',
    'uu-18-2025': 'Law of the Republic of Indonesia No. 18/2025 on National Tourism System',
    'uu-22-2009': 'Law of the Republic of Indonesia No. 22/2009 on Road Traffic and Transportation',
    'uu-39-1999': 'Law of the Republic of Indonesia No. 39/1999 on Human Rights',
    'uu-40-2008': 'Law of the Republic of Indonesia No. 40/2008 on the Elimination of Racial and Ethnic Discrimination',
    'uu-6-2011': 'Law of the Republic of Indonesia No. 6/2011 on Immigration',
    'uu-8-1999': 'Law of the Republic of Indonesia No. 8/1999 on Consumer Protection'}


TRANSLATIONS_REGULATIONS = {   'KETENTUAN_HARI_RAYA_NYEPI': {   'penalties_en': 'Reprimand and enforcement by Pecalang, customary fines (danda '
                                                     'pasikepan), and transfer to police for public disturbance.',
                                     'text_en': 'During the full 24 hours of the celebration of the Holy Day of Nyepi '
                                                '(from 06.00 WITA until 06.00 WITA the following day), all residents '
                                                'and tourists in Bali are required to observe Catur Brata Penyepian '
                                                '(four sacred religious prohibitions), which comprise:\n'
                                                '1. Amati Geni (prohibition against lighting fires, electricity, or '
                                                'any light source, including mobile phone screens outside closed '
                                                'rooms);\n'
                                                '2. Amati Karya (prohibition against working, physical labor, '
                                                'business, or operational activities, except emergency healthcare '
                                                'services);\n'
                                                '3. Amati Lelungan (prohibition against travelling, walking outside '
                                                'homes/hotels, or driving vehicles on public roads); and\n'
                                                '4. Amati Lelanguan (prohibition against entertainment, revelry, loud '
                                                'music, parties, or festive activities).\n'
                                                'Supervision and enforcement of public order during Nyepi are executed '
                                                'by Pecalang (traditional Balinese security officers) in their '
                                                'respective Desa Adat (customary village) jurisdictions. All public '
                                                'transport, sea ports, and airports (I Gusti Ngurah Rai) cease '
                                                'operations, except for emergency humanitarian and hospital '
                                                'assistance.',
                                     'title_en': 'Nyepi Observance & Catur Brata Penyepian Prohibitions',
                                     'translation_status': 'ai-assisted'},
    'PERDA_BALI_04_2019_PASAL_1': {   'penalties_en': 'Foundational statutory definitions establishing customary '
                                                      'jurisdiction and compliance obligations under Balinese '
                                                      'customary law.',
                                      'text_en': '8. Customary Village (Desa Adat) is a customary law community unit '
                                                 'in Bali possessing territory, original standing, original structure, '
                                                 'traditional rights, own wealth, traditions, social living etiquette '
                                                 'across generations bound to sacred shrines (kahyangan tiga or '
                                                 'village shrines), duties and authority as well as rights to govern '
                                                 'and manage its own affairs.\n'
                                                 '10. Krama Desa Adat (customary village villagers) are Balinese Hindu '
                                                 'citizens who are Mipil (officially registered customary members) in '
                                                 'the local Customary Village.\n'
                                                 '11. Krama Tamiu are Balinese Hindu citizens who are not Mipil, but '
                                                 'registered in the local Customary Village.\n'
                                                 '12. Tamiu are persons other than Krama Desa Adat and Krama Tamiu who '
                                                 'reside within the Customary Village territory temporarily or '
                                                 'permanently and are registered in the local Customary Village.\n'
                                                 '29. Awig-Awig is the customary regulation enacted by the Customary '
                                                 'Village and/or Banjar Adat applicable to Krama Desa Adat, Krama '
                                                 'Tamiu, and Tamiu.\n'
                                                 '30. Pararem is the rule/decision of the Customary Village Assembly '
                                                 '(Paruman Desa Adat) implementing Awig-Awig or regulating new matters '
                                                 'and/or resolving customary disputes in the Customary Village.',
                                      'title_en': 'Definitions of Desa Adat, Krama, Tamiu, Awig-Awig, and Pararem '
                                                  '(Points 8, 10-12, 29-30)',
                                      'translation_status': 'ai-assisted'},
    'PERDA_BALI_05_2020_PASAL_15': {   'penalties_en': 'Administrative sanctions, restriction of access to tourist '
                                                       'attractions, and customary restitution claims if damaging '
                                                       'sacred heritage.',
                                       'text_en': 'Every tourist visiting the Region is required to:\n'
                                                  'a. Respect the religious values, customs, traditions, arts and '
                                                  'culture, and local wisdom of the Balinese community;\n'
                                                  'b. Maintain and preserve the environment and cultural sanctity of '
                                                  'tourist attractions;\n'
                                                  'c. Prevent pollution and damage to the natural and cultural '
                                                  'environment;\n'
                                                  'd. Dress politely, properly, and respectfully when visiting tourist '
                                                  'attractions, particularly sacred places;\n'
                                                  'e. Obey all guidelines, instructions, prohibitions, and warning '
                                                  'signs placed at tourist attractions;\n'
                                                  'f. Maintain public peace, order, and decency; and\n'
                                                  'g. Participate in preventing and reporting unlawful acts, '
                                                  'violations of public order, or desecration of cultural heritage to '
                                                  'managers or competent authorities.',
                                       'title_en': 'Visitor & Tourist Obligations at Cultural Destinations (Article '
                                                   '15)',
                                       'translation_status': 'ai-assisted'},
    'PERDA_BALI_05_2020_PASAL_25': {   'penalties_en': 'Exclusion from the official Bali Digital Tourism single portal '
                                                       'and revocation of verified partner status.',
                                       'text_en': '(1) The implementation of digital Balinese cultural tourism '
                                                  'includes: a. Tourism inspiration; b. tourist arrival; c. tourism '
                                                  'destinations and activities; d. post-visit tourist engagement; e. '
                                                  'Bali Tourism Single-Door Portal; and f. digital documentation of '
                                                  'Balinese Cultural Tourism. (2) Tourism inspiration as referred to '
                                                  'in paragraph (1) letter a includes: a. Digital Tourism '
                                                  'Destinations; b. live broadcasting of attractions for Sad Kerthi '
                                                  'environment, arts, and culture; c. digital tourism utilizing '
                                                  'augmented reality and virtual reality technologies; d. smart tour '
                                                  'package information; e. digital tourism promotion; and f. other '
                                                  'digital technologies providing inspiration for Balinese Cultural '
                                                  'Tourism. (3) Tourist arrival as referred to in paragraph (1) letter '
                                                  'b includes: a. electronic membership (e-membership) for Bali '
                                                  'Digital Tourism; b. digital guidance technologies for arriving '
                                                  'tourists; c. digital technologies for Integrated Tourist Security '
                                                  'Systems; d. digital hotel reservation services; e. digital online '
                                                  'transport services and Customary Village (Desa Adat) transport; f. '
                                                  'Bali Tourism digital marketplace; and g. other digital technologies '
                                                  'or services for arriving Tourists. (4) Tourism destinations and '
                                                  'activities as referred to in paragraph (1) letter c include: a. '
                                                  'electronic ticketing (e-ticketing) for tourist destinations and '
                                                  'performances; b. digital guiding and exploration technologies for '
                                                  'destinations; c. touchscreen presentations for sacred sites and '
                                                  'rituals; d. cashless closed tourism ecosystem services integrated '
                                                  'with hotel and restaurant tax systems; e. reward-based tourist '
                                                  'destination reviews; and f. other digital technologies for tourist '
                                                  'destinations and activities. (5) Post-trip tourist engagement with '
                                                  'integrated customer relationship management includes: a. Tourist '
                                                  'satisfaction index; b. Tourist loyalty programs; and c. Tourist '
                                                  'reward systems.',
                                       'title_en': 'Digital Cultural Tourism Governance & Technologies',
                                       'translation_status': 'ai-assisted'},
    'PERDA_BALI_05_2020_PASAL_26': {   'penalties_en': 'Non-compliant tourism operators barred from participating in '
                                                       'official regional marketing and booking integration.',
                                       'text_en': '(1) The Governor shall establish the Bali Tourism Single-Door '
                                                  'Portal to integrate all tourism stakeholders comprising tourism '
                                                  'business enterprises, government, and society. (2) The Bali Tourism '
                                                  'Single-Door Portal as referred to in paragraph (1) encompasses: a. '
                                                  'hotel/accommodation reservations; b. electronic ticketing '
                                                  '(e-ticketing) for tourist destinations; c. online transportation; '
                                                  'd. Bali Tourism digital marketplace; e. cashless payment '
                                                  'integration; and f. other fields in accordance with developments in '
                                                  'the Bali tourism industry. (3) Provisions regarding the Bali '
                                                  'Tourism Single-Door Portal as referred to in paragraph (2) shall be '
                                                  'regulated in a Governor Regulation.',
                                       'title_en': 'Bali Tourism Single-Door Portal (Portal Satu Pintu)',
                                       'translation_status': 'ai-assisted'},
    'PERDA_BALI_05_2020_PASAL_6': {   'penalties_en': 'Administrative sanctions, written warning, and temporary '
                                                      'closure or suspension of destination operational permits.',
                                      'text_en': '(1) Managers of Tourist Attractions (DTW) are required to satisfy '
                                                 'standards including: a. natural DTW, cultural DTW, and spiritual DTW '
                                                 'must possess a legal corporate entity or be designated by '
                                                 'Regent/Mayor decree; and b. man-made DTW must possess a legal '
                                                 'corporate entity. (2) Managers of Tourist Attractions (DTW) are '
                                                 'required to satisfy standards including: a. prioritizing local '
                                                 'resources; b. providing information boards and code of conduct for '
                                                 'entry, at minimum in 3 (three) languages: Balinese, Indonesian, and '
                                                 'English; c. having designated information officers; d. having '
                                                 'informational materials regarding the attraction; e. having first '
                                                 'aid facilities; f. having ticket counters; g. having security '
                                                 'personnel; h. having parking management staff; i. having sanitation '
                                                 'and cleaning staff; j. providing facilities for persons with '
                                                 'disabilities; k. providing parking facilities; l. providing adequate '
                                                 'waste bins and waste management facilities; m. providing public '
                                                 'toilets fulfilling standards of cleanliness, health, safety, and '
                                                 'comfort; and n. maintaining supporting amenities such as artshops, '
                                                 'restaurants, food stalls, situated adjacent to the parking area. (3) '
                                                 'Beyond meeting the standards referred to in paragraph (2), Managers '
                                                 'of natural DTW must satisfy additional standards: a. implementing '
                                                 'security, safety, and health standards for Tourists; b. providing '
                                                 'safety and security signage; and c. protecting and conserving the '
                                                 'natural DTW environment. (4) Beyond meeting the standards referred '
                                                 'to in paragraph (2), Managers of man-made DTW must satisfy '
                                                 'additional standards: a. observing local wisdom; b. maintaining '
                                                 'harmony with surrounding communities; c. establishing standard '
                                                 'operating procedures; d. providing spaces for promotion and '
                                                 'marketing of local products; e. providing health facilities; f. '
                                                 'having separate entry and exit pathways; and g. providing '
                                                 'comfortable waiting rooms adjacent to parking areas.',
                                      'title_en': 'DTW Management Standards & Tri-Lingual Signage Requirements',
                                      'translation_status': 'ai-assisted'},
    'PERDA_BALI_05_2020_PASAL_7': {   'penalties_en': 'Revocation of operational license, obligation to perform '
                                                      'Ngayap/Tepung Tawar customary purification ceremonies, and '
                                                      'criminal referral.',
                                      'text_en': '(1) Every person is prohibited from damaging partial or entire '
                                                 'physical and non-physical elements of Tourist Attractions (DTW). (2) '
                                                 'Every person is prohibited from utilizing Pura (temples), Pratima '
                                                 '(sacred effigies), religious symbols, or sanctified sacred objects '
                                                 'solely as tourist attractions. (3) Every person is prohibited from '
                                                 'erecting structures or objects that obstruct or disturb visual '
                                                 'viewscapes or cultural landscapes (saujana) designated as Tourist '
                                                 'Attractions.',
                                      'title_en': 'Prohibition of Desecration or Damage to Tourist Destinations & '
                                                  'Sacred Sites',
                                      'translation_status': 'ai-assisted'},
    'PERDA_BALI_06_2023_LEVY': {   'penalties_en': 'Verbal reprimand, written warning, and denial of services at '
                                                   'Tourist Attractions (DTW).',
                                   'text_en': 'Pasal 4A\n'
                                              '(1) Foreign Tourists entering Bali directly from abroad or indirectly '
                                              'via other territories in Indonesia are required to pay a Foreign '
                                              'Tourist Levy in accordance with legislative provisions.\n'
                                              '(2) The Levy referred to in paragraph (1) is exempted for Foreign '
                                              'Nationals comprising: a. crew on transport conveyances; b. holders of '
                                              'Limited Stay Permits (KITAS) or Permanent Stay Permits (KITAP); c. '
                                              'holders of diplomatic and service visas; d. holders of family '
                                              'reunification visas; e. holders of student visas; f. holders of golden '
                                              'visas; and g. holders of other visa types.\n'
                                              '(3) Exemption grounds referred to in paragraph (2) pertain to official '
                                              'duties, citizenship status, and/or proven benefit to the development of '
                                              'Bali or Indonesia.\n'
                                              '(4) Further provisions regarding levy payment exemptions are regulated '
                                              'in a Governor Regulation.\n'
                                              '\n'
                                              'Pasal 5\n'
                                              '(1) Payment of the Foreign Tourist Levy referred to in Pasal 4A applies '
                                              "throughout the tourist's visit in Bali prior to departing Indonesian "
                                              'territory.\n'
                                              '(2) The Foreign Tourist Levy referred to in paragraph (1) is conducted '
                                              'non-cash (cashless) through electronic payment means (e-Payment) in the '
                                              'amount of Rp150.000,00 (seratus lima puluh ribu rupiah).\n'
                                              '(3) Payment of the Levy referred to in paragraph (1) is made prior to '
                                              'or during travel in Bali.\n'
                                              '(4) Payment of the Levy referred to in paragraph (3) is deposited into '
                                              'the Regional General Cash Account (RKUD).\n'
                                              '(5) Payment of the Levy referred to in paragraph (3) is issued an '
                                              'electronic receipt of payment and/or designated official verification '
                                              'mark from the Provincial Government.\n'
                                              '(6) Provisions regarding payment procedures are regulated in a Governor '
                                              'Regulation.\n'
                                              '\n'
                                              'Pasal 16A\n'
                                              '(1) Every Foreign Tourist traveling in Bali violating the provisions of '
                                              'Pasal 4A paragraph (1) is subject to administrative sanctions.\n'
                                              '(2) Administrative sanctions referred to in paragraph (1) comprise: a. '
                                              'verbal reprimand; b. written warning delivered to the person concerned; '
                                              'and/or c. denial of service at Tourist Attractions (DTW).\n'
                                              '(3) The mechanism for imposing administrative sanctions referred to in '
                                              'paragraph (2) is implemented in accordance with statutory regulations.',
                                   'title_en': 'Foreign Tourist Levy Mandate & Sanctions (Articles 4A, 5, 16A)',
                                   'translation_status': 'ai-assisted'},
    'PERDA_BALI_06_2023_PASAL_12': {   'penalties_en': 'Statutory entitlement outlining tourist rights to cultural '
                                                       'preservation, safety, and transparent accounting.',
                                       'text_en': 'Foreign Tourists obtain benefits from paid levies in the form of: '
                                                  'a. cultural-based, quality, and dignified Bali Tourism governance; '
                                                  'b. well-managed preservation of customs, traditions, arts, culture, '
                                                  'and local wisdom with spiritual aura (metaksu); c. a cleaner, more '
                                                  'beautiful, and holistically sustainable Natural Environment; d. '
                                                  'cleanliness, order, comfort, and security during stay in Bali; e. '
                                                  'quality public transportation infrastructure and facilities; f. '
                                                  'enhanced comprehensive, integrated, and up-to-date Bali Cultural '
                                                  'Tourism information services; g. disaster management services; and '
                                                  'h. transparent and accountable reporting from the Provincial '
                                                  'Government regarding revenues and expenditure for Culture and '
                                                  'Natural Environment protection.',
                                       'title_en': 'Foreign Tourist Entitlements & Levy Benefits',
                                       'translation_status': 'ai-assisted'},
    'PERDA_BALI_06_2023_PASAL_14': {   'penalties_en': 'Internal government oversight and inter-agency enforcement '
                                                       'mechanisms for tourist levy compliance.',
                                       'text_en': '(1) The Governor conducts guidance and supervision over the '
                                                  'implementation of the Foreign Tourist Levy collection. (2) Guidance '
                                                  'referred to in paragraph (1) is conducted by Regional Apparatus '
                                                  'administering government affairs in tourism. (3) Supervision over '
                                                  'the Foreign Tourist Levy referred to in paragraph (1) is conducted '
                                                  'by Provincial Government Internal Supervisory Apparatus. (4) The '
                                                  'Governor may establish an Integrated Team in conducting guidance '
                                                  'and supervision referred to in paragraph (1).',
                                       'title_en': 'Provincial Guidance, Audit & Integrated Task Force Oversight',
                                       'translation_status': 'ai-assisted'},
    'PERDA_BALI_06_2023_PENJELASAN_UMUM': {   'penalties_en': 'Official legislative intent establishing the reciprocal '
                                                              'principle and anti-corruption fiduciary standard for '
                                                              'levy fund management.',
                                              'text_en': 'To overcome the constraint of limited fiscal space in '
                                                         'efforts to protect Balinese Culture and Natural Environment, '
                                                         'Pasal 8 paragraph (3) and paragraph (4) of Law Number 15 '
                                                         'Year 2023 on Bali Province granted authority to the Regional '
                                                         'Government of Bali Province to obtain funding sources in the '
                                                         'form of a Foreign Tourist Levy visiting Bali, governed by '
                                                         'regional regulations. This levy authority aligns with Pasal '
                                                         '3 of Bali Provincial Regional Regulation Number 12 Year 2022 '
                                                         'on the Management of Segregated Regional Wealth and Other '
                                                         'Legitimate Regional Original Revenue, designating lawful '
                                                         'regional revenue point v as other income according to '
                                                         'statutory provisions. With this potential, the Provincial '
                                                         'Government is expected to administer cultural-based, '
                                                         'quality, and dignified tourism through good, competitive, '
                                                         'and sustainable governance. The active role of Foreign '
                                                         'Tourists contributing to culture and natural protection '
                                                         'accords with the principle of fair reciprocity. All who love '
                                                         'Bali should care and participate in protecting culture, '
                                                         'environment, and transportation infrastructure. The '
                                                         'Provincial Government manages levy funds in a planned, '
                                                         'directed, targeted, transparent, accountable, and '
                                                         'corruption-free manner under statutory regulations. This '
                                                         "fosters Foreign Tourists' trust that funds submitted are "
                                                         'utilized effectively for public tourism services and '
                                                         'infrastructure during their stay in Bali.',
                                              'title_en': 'General Elucidation on the Foreign Tourist Levy & Culture '
                                                          'Protection',
                                              'translation_status': 'ai-assisted'},
    'PERGUB_BALI_02_2024_PASAL_11': {   'penalties_en': 'Entry denied or digital inspection red flag at arrival '
                                                        'checkpoints if digital proof is absent.',
                                        'text_en': '(1) Payment of the Levy shall be made prior to entering entry '
                                                   'arrival gates into Bali. (2) Payment as referred to in paragraph '
                                                   '(1) shall be conducted through the Love Bali System or other '
                                                   'systems integrated with the Love Bali System. (3) Payment of the '
                                                   'Levy through the Love Bali System as referred to in paragraph (2) '
                                                   'shall be carried out via the following flow: a. Foreign Tourists '
                                                   'access the Love Bali System to fill in data as referred to in '
                                                   'Pasal 9 paragraph (2) and process payment; b. Foreign Tourists '
                                                   'select the payment method to be used, such as credit card, bank '
                                                   'transfer, virtual account, or QRIS; and c. The Love Bali System '
                                                   'provides payment status notification and proof of payment to the '
                                                   'respective Foreign Tourist in digital or physical format.',
                                        'title_en': 'Levy Payment Flow & Digital Verification (Love Bali)',
                                        'translation_status': 'ai-assisted'},
    'PERGUB_BALI_02_2024_PASAL_6': {   'penalties_en': 'Revocation of exemption status and obligation to pay standard '
                                                       'levy if eligibility criteria are not met.',
                                       'text_en': '(1) Foreign Tourists exempted from paying the Levy as referred to '
                                                  'in Pasal 5 paragraph (1) comprise: a. holders of diplomatic and '
                                                  'official service visas; b. conveyance crew; c. holders of Limited '
                                                  'Stay Permits (KITAS) or Permanent Stay Permits (KITAP); d. holders '
                                                  'of family reunification visas; e. holders of student visas; f. '
                                                  'holders of golden visas; and g. holders of other visa types. (2) '
                                                  'Exemption grounds as referred to in paragraph (1) pertain to '
                                                  'official state duties, citizenship status, and/or proven benefit to '
                                                  'the development of Bali or the Indonesian State.',
                                       'title_en': 'Tourist Levy Waiver Categories & Criteria',
                                       'translation_status': 'ai-assisted'},
    'PERGUB_BALI_02_2024_PASAL_7': {   'penalties_en': 'Rejection of exemption application, requiring payment of '
                                                       'standard levy prior to entry.',
                                       'text_en': '(1) Foreign Tourists exempted from paying the Levy as referred to '
                                                  'in Pasal 6 paragraph (1) points f and g shall submit an application '
                                                  'by completing all requirements specified within the Love Bali '
                                                  'System. (2) Applications for levy exemption as referred to in '
                                                  'paragraph (1) must be submitted at least 5 (five) days prior to '
                                                  'arrival at Bali entry gates. (3) Regional Apparatus administering '
                                                  'tourism affairs shall verify and grant approval or rejection of '
                                                  'applications referred to in paragraph (2) within a maximum of 3 '
                                                  '(three) days upon receipt. (4) Approvals or rejections as referred '
                                                  'to in paragraph (3) shall be communicated to the respective Foreign '
                                                  'Tourist via the Love Bali System.',
                                       'title_en': 'Levy Exemption Application Procedures (Love Bali)',
                                       'translation_status': 'ai-assisted'},
    'PERGUB_BALI_25_2020_PASAL_10': {   'penalties_en': 'Customary warning, removal from temple grounds, and '
                                                        'civil/criminal liability for unauthorized alterations.',
                                        'text_en': '(1) Safeguarding of Pura as referred to in Pasal 5 paragraph (1) '
                                                   'letter a, letter b, letter c, letter d, and letter e is conducted '
                                                   'to prevent damage, desecration, profanation, and misuse of Pura. '
                                                   '(2) Safeguarding of Pura as referred to in paragraph (1) is '
                                                   'carried out by Pengempon Pura (temple custodians) in cooperation '
                                                   'with the Customary Village (Desa Adat) and Regional Apparatus. (3) '
                                                   'Safeguarding of Pura as referred to in paragraph (1) is carried '
                                                   'out by preserving the existence of Pura possessing historical '
                                                   'value and/or suspected cultural heritage vestiges. (4) '
                                                   'Preservation as referred to in paragraph (3) is proactively '
                                                   'conducted by Pengempon or the public by reporting Pura possessing '
                                                   'historical value and/or suspected cultural heritage vestiges to '
                                                   'relevant institutions. (5) Every Hindu follower may participate in '
                                                   'safeguarding Pura upon receiving authorization from Pengempon '
                                                   'Pura, the Customary Village, and Regional Apparatus.',
                                        'title_en': 'Proactive Security & Community Protection of Temples',
                                        'translation_status': 'ai-assisted'},
    'PERGUB_BALI_25_2020_PASAL_3_4': {   'penalties_en': 'Administrative revocation of regional financial support and '
                                                         'exclusion from government preservation grants.',
                                         'text_en': 'The scope of this Governor Regulation encompasses: a. '
                                                    'facilitation of Pura protection; b. facilitation of Pratima '
                                                    'protection; c. facilitation of Religious Symbol protection; d. '
                                                    'prohibitions and sanctions; e. awards and recognition; f. '
                                                    'guidance, supervision, and coordination; and g. funding. Pasal 4 '
                                                    'Facilitation of the Protection of Pura, Pratima, and Religious '
                                                    'Symbols as referred to in Pasal 3 letter a, letter b, and letter '
                                                    'c is executed through: a. inventorying; b. securing; c. '
                                                    'maintenance; d. safeguarding and salvage; and e. publication.',
                                         'title_en': 'Scope & Methods of Sacred Temple Protection Facilitation',
                                         'translation_status': 'ai-assisted'},
    'PERGUB_BALI_25_2020_PASAL_45_46': {   'penalties_en': 'Customary sanctions (Arta danda/fine, Pengaksama '
                                                           'danda/apology, Sangaskara danda/purification ritual) and '
                                                           'criminal referral.',
                                           'text_en': 'Pasal 45\n'
                                                      '(1) Entry into Pura (temples) is prohibited for: a. Every '
                                                      'person in a state of Cuntaka or Sebel (spiritual impurity); and '
                                                      'b. Every person not directly participating in a prayer '
                                                      'ceremony, piodalan (temple anniversary), and/or temple '
                                                      'preservation activity.\n'
                                                      '(2) Every person is prohibited from damaging and desecrating '
                                                      'Pura.\n'
                                                      '(3) Every person is prohibited from damaging and stealing '
                                                      'Pratima (sacred effigies).\n'
                                                      '(4) Every person is prohibited from damaging, stealing, '
                                                      'desecrating, and misusing Religious Symbols.\n'
                                                      '\n'
                                                      'Pasal 46\n'
                                                      '(1) Every person violating the prohibitions referred to in '
                                                      'Pasal 45 is subject to customary sanctions.\n'
                                                      '(2) Every person violating the prohibitions referred to in '
                                                      'Pasal 45 paragraph (2), paragraph (3), and paragraph (4) is '
                                                      'subject to sanctions under statutory provisions.\n'
                                                      '(3) Customary sanctions referred to in paragraph (1) comprise: '
                                                      'a. Arta danda (fine); b. Pengaksama danda (apology); and c. '
                                                      'Sangaskara danda (purification ceremony).\n'
                                                      '(4) Imposition of customary sanctions referred to in paragraph '
                                                      '(3) is executed by Customary Villages (Desa Adat) and/or '
                                                      'Pengempon Pura (temple custodians).',
                                           'title_en': 'Temple Protection Prohibitions & Customary Sanctions (Articles '
                                                       '45 & 46)',
                                           'translation_status': 'ai-assisted'},
    'PERGUB_BALI_25_2025_PASAL_9_12': {   'penalties_en': 'Payment verification scan failure results in redirection to '
                                                          'on-site digital payment counters before gate entry.',
                                          'text_en': 'Pasal 9\n'
                                                     '(1) Payment of the Levy is carried out through the Love Bali '
                                                     'official digital system or integrated payment channels before or '
                                                     'upon arrival at entry points.\n'
                                                     '(2) Payment data includes passport identity, date of arrival, '
                                                     'flight/vessel information, and electronic contact details of the '
                                                     'Foreign Tourist.\n'
                                                     '(3) Evidence of payment is issued in the form of a digital levy '
                                                     'voucher containing a unique QR code.\n'
                                                     '\n'
                                                     'Pasal 12\n'
                                                     '(1) Verification of the Levy payment is carried out by '
                                                     'designated inspection officers using digital scanner devices.\n'
                                                     '(2) Verification locations include arrival terminals at '
                                                     'international airports, domestic arrival terminals, seaports, '
                                                     'and entrance checkpoints at tourist attractions across Bali.\n'
                                                     '(3) Foreign Tourists who have not completed payment are directed '
                                                     'to make immediate payment via official digital payment points '
                                                     'on-site.',
                                          'title_en': 'Digital Payment Flow & Verification Procedures (Articles 9 & '
                                                      '12)',
                                          'translation_status': 'ai-assisted'},
    'SE_GUB_04_2023_DO': {   'penalties_en': 'Verbal reprimand, termination of tour visit, customary village '
                                             'sanctions, and report to Immigration authorities.',
                             'text_en': 'Foreign Tourists visiting Bali are required to: 1. Revere the sanctity of '
                                        'Pura (Balinese Hindu temples), Pratima (sacred effigies), and religious '
                                        'symbols that are sanctified; 2. Dress modestly, appropriately, and '
                                        'respectfully when visiting sacred places, tourist attractions, and public '
                                        'areas in Bali; 3. Behave respectfully in sacred areas, tourist zones, '
                                        'restaurants, shopping centers, roadways, and other public venues; 4. Be '
                                        'accompanied by a licensed tour guide when visiting tourist attractions; 5. '
                                        'Conduct foreign currency exchange at official licensed money changers '
                                        '(authorized by Bank Indonesia); 6. Make payments using Quick Response Code '
                                        'Indonesian Standard (QRIS) or Rupiah currency; 7. Comply with the prevailing '
                                        'traffic laws and regulations in Indonesia.',
                             'title_en': "Foreign Tourist Obligations / Do's (Points 1 to 7)",
                             'translation_status': 'ai-assisted'},
    'SE_GUB_04_2023_DONT': {   'penalties_en': 'Criminal prosecution, customary restitution fines (purification '
                                               'ceremony/prayascitta), and deportation with international entry '
                                               'blacklisting.',
                               'text_en': 'Foreign Tourists are prohibited from:\n'
                                          '1. Entering the Utama Mandala (innermost sacred sanctuary) and Madya '
                                          'Mandala (middle sanctuary) of sacred places or Pura (Balinese Hindu '
                                          'temples) except for prayer by wearing Balinese traditional attire and not '
                                          'during menstruation (period);\n'
                                          '2. Climbing sacred trees;\n'
                                          '3. Conducting behavior that desecrates sacred places, Pura (Balinese Hindu '
                                          'temples), Pratima (sacred effigies), and religious symbols, such as taking '
                                          'photos in inappropriate attire or nude;\n'
                                          '4. Littering and/or polluting lakes, springs, rivers, seas, and public '
                                          'places;\n'
                                          '5. Using single-use plastics such as plastic bags, polystyrene (styrofoam), '
                                          'and plastic straws;\n'
                                          '6. Uttering harsh words, behaving impolitely, making noise, and acting '
                                          'aggressively toward state apparatus, government, local communities, or '
                                          'fellow tourists, either directly or indirectly through social media;\n'
                                          '7. Working and/or conducting business activities illegally without '
                                          'possessing official documents issued by competent authorities; and\n'
                                          '8. Engaging in illegal activities such as trading illegal goods, flora and '
                                          'fauna, sacred cultural artifacts, and illicit narcotics.',
                               'title_en': "Foreign Tourist Prohibitions / Don'ts (Points 2.a to 2.h)",
                               'translation_status': 'ai-assisted'},
    'UU_01_2023_PASAL_242': {   'penalties_en': 'Imprisonment for a maximum of 3 years or category IV fine (up to '
                                                'Rp200,000,000).',
                                'text_en': 'Any Person who in Public expresses feelings of hostility, hatred, or '
                                           'contempt toward one or several groups or classes of the Indonesian '
                                           'population based on race, nationality, ethnicity, skin color, gender, '
                                           'mental disability, or physical disability, shall be sentenced to '
                                           'imprisonment for a maximum of 3 (tiga) years or a category IV fine.',
                                'title_en': 'Criminal Prohibition of Public Expression of Hostility & Contempt',
                                'translation_status': 'ai-assisted'},
    'UU_01_2023_PASAL_243': {   'penalties_en': 'Imprisonment for a maximum of 4 years or category IV fine.',
                                'text_en': '(1) Any Person who broadcasts, exhibits, or affixes writings or images so '
                                           'that they are visible to the public or plays recordings so that they are '
                                           'audible to the public or disseminates through information technology '
                                           'means, containing expressions of hostility with the intent that their '
                                           'content be known or more widely known to the public, toward one or several '
                                           'groups or classes of the Indonesian population based on race, nationality, '
                                           'ethnicity, skin color, religion, belief, gender, mental disability, or '
                                           'physical disability that results in the occurrence of Violence against '
                                           'persons or Property, shall be sentenced to imprisonment for a maximum of 4 '
                                           '(empat) years or a category IV fine.',
                                'title_en': 'Criminal Penalties for Disseminating Hate Content Leading to Violence',
                                'translation_status': 'ai-assisted'},
    'UU_01_2023_PASAL_244_245': {   'penalties_en': 'Imprisonment up to 1 year or category III fine; violent crimes '
                                                    'incur sentence enhanced by one-third (1/3).',
                                    'text_en': 'Pasal 244: Any Person who conducts distinction, exclusion, '
                                               'restriction, or preference based on race and ethnicity that results in '
                                               'the revocation or impairment of the recognition, enjoyment, or '
                                               'exercise of human rights and fundamental freedoms on equal terms in '
                                               'the civil, political, economic, social, and cultural fields, shall be '
                                               'sentenced to imprisonment for a maximum of 1 (satu) year or a category '
                                               'III fine. Pasal 245: Any Person who commits deprivation of life, '
                                               'assault, rape, lewd acts, theft with Violence, or deprivation of '
                                               'liberty grounded in racial and ethnic discrimination, may have their '
                                               'penalty increased by 1/3 (satu per tiga).',
                                    'title_en': 'Criminal Penalties for Discriminatory Acts & Enhanced Penalties for '
                                                'Violence',
                                    'translation_status': 'ai-assisted'},
    'UU_01_2024_PASAL_28_2': {   'penalties_en': 'Imprisonment up to 6 years and/or fine up to Rp1,000,000,000 under '
                                                 'Pasal 45A paragraph (2) of the ITE Law.',
                                 'text_en': 'Any Person who intentionally and without authorization distributes and/or '
                                            'transmits Electronic Information and/or Electronic Documents that are '
                                            'instigative, solicitous, or inciting in nature toward other persons so as '
                                            'to provoke feelings of hatred or hostility against specific individuals '
                                            'and/or community groups based on race, nationality, ethnicity, skin '
                                            'color, religion, belief, gender, mental disability, or physical '
                                            'disability.',
                                 'title_en': 'Prohibition of Electronic Hate Speech & Incitement (ITE Law)',
                                 'translation_status': 'ai-assisted'},
    'UU_01_2024_PASAL_45A_2': {   'penalties_en': 'Imprisonment for a maximum of 6 years and/or a maximum fine of '
                                                  'Rp1,000,000,000.',
                                  'text_en': 'Any Person who fulfills the elements referred to in Pasal 28 paragraph '
                                             '(2) shall be sentenced to imprisonment for a maximum of 6 (enam) years '
                                             'and/or a fine of at most Rp1.000.000.000,00 (satu miliar rupiah).',
                                  'title_en': 'Criminal Penalties for Electronic Hate Speech & Hostility (ITE Law)',
                                  'translation_status': 'ai-assisted'},
    'UU_06_2011_PASAL_75': {   'penalties_en': 'Immediate deportation to country of origin and placement on the entry '
                                               'prohibition (blacklist) roster into Indonesia.',
                               'text_en': '(1) Immigration Officers are authorized to carry out Immigration '
                                          'Administrative Measures against Foreigners residing within Indonesian '
                                          'Territory who carry out dangerous activities and are reasonably suspected '
                                          'of endangering public security and order, or not respecting or not obeying '
                                          'statutory laws and regulations.\n'
                                          '(2) Immigration Administrative Measures as referred to in paragraph (1) may '
                                          'take the form of:\n'
                                          'a. inclusion in the prevention or deterrence list;\n'
                                          'b. restriction, change, or cancellation of Residence Permits;\n'
                                          'c. prohibition from being in one or several certain places in Indonesian '
                                          'Territory;\n'
                                          'd. obligation to reside in a certain place in Indonesian Territory;\n'
                                          'e. imposition of fines; and/or\n'
                                          'f. Deportation from Indonesian Territory.',
                               'title_en': 'Immigration Administrative Sanctions & Deportation (Article 75)',
                               'translation_status': 'ai-assisted'},
    'UU_08_1999_PASAL_4G': {   'penalties_en': 'Administrative sanctions, compensation orders, and civil litigation '
                                               'under Consumer Protection Law.',
                               'text_en': 'Consumer rights comprise: a. the right to comfort, security, and safety in '
                                          'consuming goods and/or services; b. the right to choose goods and/or '
                                          'services and to obtain said goods and/or services in accordance with the '
                                          'exchange rate and promised conditions and guarantees; c. the right to true, '
                                          'clear, and honest information regarding the condition and guarantee of '
                                          'goods and/or services; d. the right to have opinions and grievances heard '
                                          'regarding the goods and/or services used; e. the right to obtain proper '
                                          'advocacy, protection, and dispute settlement efforts in consumer '
                                          'protection; f. the right to consumer education and counseling; g. the right '
                                          'to be treated or served properly and honestly without discrimination; h. '
                                          'the right to obtain compensation, redress, and/or reimbursement if the '
                                          'goods and/or services received do not conform to agreement or proper '
                                          'conditions; i. rights regulated under other legislative provisions.',
                               'title_en': 'Consumer Rights to Fair & Non-Discriminatory Service',
                               'translation_status': 'ai-assisted'},
    'UU_15_2023_PASAL_8': {   'penalties_en': 'Does not establish criminal sanctions; administrative and financial '
                                              'oversight governed by regional legislation.',
                              'text_en': '(3) In addition to funding sources as referred to in paragraph (1), in the '
                                         'framework of protecting the culture and natural environment of Bali, the '
                                         'Regional Government of Bali Province is authorized to obtain funding sources '
                                         'from:\n'
                                         'a. contributions from lawful and non-binding sources;\n'
                                         'b. foreign tourist levy; and/or\n'
                                         'c. other legitimate income in accordance with statutory regulations.\n'
                                         '(4) Further provisions regarding the foreign tourist levy as referred to in '
                                         'paragraph (3) letter b shall be regulated by a Regional Regulation of Bali '
                                         'Province.',
                              'title_en': 'Statutory Authority for Bali Provincial Levy (Article 8)',
                              'translation_status': 'ai-assisted'},
    'UU_18_2025_PASAL_1': {   'penalties_en': 'Statutory definitions under national tourism law.',
                              'text_en': '6. Tourism Destination Area, hereinafter referred to as Tourism Destination, '
                                         'is a geographical area located within one or more administrative regions '
                                         'containing tourism attractions, public facilities, tourism facilities, '
                                         'accessibility, and mutually interrelated communities realizing Tourism. 7. '
                                         'Tourism Attraction is anything possessing uniqueness, beauty, and value in '
                                         'the form of diversity of natural wealth, culture, and man-made heritage that '
                                         'is the target or destination of tourist visits. 8. Cultural Heritage is '
                                         'relics and/or practices, representations, expressions, knowledge, artifact '
                                         'objects, and cultural spaces tangible and/or intangible representing value '
                                         'systems, knowledge, beliefs, traditions, cultural expressions, styles, and '
                                         'vestiges of a culture inherited and/or transmitted from one generation to '
                                         'the next or passed down from the past to the present, requiring preservation '
                                         'due to significant value for science, education, history, religion, and/or '
                                         'culture. 9. Tourism Business is an enterprise providing goods and/or '
                                         'services to meet tourist needs and organize Tourism. 10. Tourism Industry is '
                                         'a collective of interrelated Tourism Businesses generating goods and/or '
                                         'services to satisfy tourist needs in organizing Tourism. 11. Strategic '
                                         'Tourism Area is an area having primary functions in Tourism or possessing '
                                         'potential for Tourism development that exerts significant influence in one '
                                         'or more aspects, such as economic growth, social and cultural vitality, '
                                         'natural resource empowerment, environmental carrying capacity, and national '
                                         'defense.',
                              'title_en': 'Statutory Definitions of Tourism Destination, Attraction, Heritage, '
                                          'Industry & Strategic Areas (Points 6-11)',
                              'translation_status': 'ai-assisted'},
    'UU_18_2025_PASAL_11G': {   'penalties_en': 'Guaranteed priority access for local workforce, consignment, and '
                                                'management.',
                                'text_en': 'Pasal 11G Communities in the vicinity of Tourism Destinations have '
                                           'priority opportunities to: a. become Tourism workers; b. obtain '
                                           'consignment opportunities; c. manage Tourism; d. obtain information '
                                           'regarding tourism development and expansion activities in their area; '
                                           'and/or e. obtain protection over religious and cultural norms.',
                                'title_en': 'Priority Opportunities for Communities Adjacent to Tourism Destinations '
                                            '(Article 11G)',
                                'translation_status': 'ai-assisted'},
    'UU_18_2025_PASAL_17P': {   'penalties_en': 'Loss of official tourism village designation or administrative '
                                                'non-eligibility for regional promotion.',
                                'text_en': '(1) Tourism Villages or Tourism Hamlets as referred to in Pasal 17O '
                                           'constitute areas possessing authentic and distinctive Tourism Attraction '
                                           'potential presented within a community life structure integrated with the '
                                           'customs and traditions of rural or hamlet communities in all their '
                                           'potential. (2) Development of Tourism Villages or Tourism Hamlets aims to: '
                                           'a. preserve local cultural values; b. promote regional development and '
                                           'welfare of village and sub-district communities; c. reduce poverty and '
                                           'unemployment; d. improve the quality of residential environments; e. '
                                           'leverage local wisdom in managing potential and resolving environmental '
                                           'challenges; f. expand tourism destinations or create new Tourism '
                                           'Destinations; g. accelerate integrated village and sub-district '
                                           'development; and h. foster empowerment of women, Persons with '
                                           'Disabilities, and other vulnerable groups. (3) Criteria for Tourism '
                                           'Villages or Tourism Hamlets include: a. possessing authentic and '
                                           'compelling Tourism Attraction potential; b. having an engaged local '
                                           'community dedicated to and connected with the Tourism Attractions in their '
                                           'area; and c. availability of infrastructure fulfilling tourist needs in '
                                           'alignment with local wisdom.',
                                'title_en': 'Tourism Village Provisions (Definition, Objectives, Criteria)',
                                'translation_status': 'ai-assisted'},
    'UU_18_2025_PASAL_22': {   'penalties_en': 'Guaranteed legal standing and equal protection for licensed tourism '
                                               'businesses under national law.',
                               'text_en': 'Every Tourism Business Operator has the right to: a. obtain equal '
                                          'opportunities in doing business in the Tourism sector; b. establish and '
                                          'become members of Tourism associations; c. obtain accurate information for '
                                          'doing business in a Tourism Destination; d. develop Tourism Businesses '
                                          'digitally; e. obtain legal protection and security in business; and f. '
                                          'obtain facilities and convenience in conducting business in accordance with '
                                          'statutory regulations.',
                               'title_en': 'Statutory Rights of Tourism Business Operators',
                               'translation_status': 'ai-assisted'},
    'UU_18_2025_PASAL_25': {   'penalties_en': 'Administrative warning, removal from destination, liability for '
                                               'damage, and referral for law enforcement.',
                               'text_en': 'Every Tourist is obligated to: a. maintain and respect religious norms, '
                                          'customs, culture, history, and values living in local communities; b. '
                                          'fulfill rules and requirements specified when entering a Tourism '
                                          'Destination; c. preserve and conserve the environment; d. maintain order, '
                                          'security, and comfort of the environment around Tourism Destinations; e. '
                                          'preserve the physical integrity of Tourism Attractions; f. preserve the '
                                          'uniqueness, beauty, and authentic value of a Tourism Attraction; and g. '
                                          'prevent all forms of acts violating decency and activities violating the '
                                          'law.',
                               'title_en': 'General Tourist Obligations (Cultural Respect, Decency, Preservation)',
                               'translation_status': 'ai-assisted'},
    'UU_18_2025_PASAL_57A': {   'penalties_en': 'Statutory enabling clause for national tourist levy management and '
                                                'tourism fund allocation.',
                                'text_en': '(1) The Government may collect a levy from foreign Tourists. (2) The levy '
                                           'referred to in paragraph (1) is managed and utilized for Tourism '
                                           'development activities. (3) Further provisions regarding procedures for '
                                           'collecting the levy referred to in paragraph (1) and management and '
                                           'utilization referred to in paragraph (2) are regulated by Government '
                                           'Regulation.',
                                'title_en': 'Central Government Foreign Tourist Levy Authority',
                                'translation_status': 'ai-assisted'},
    'UU_18_2025_PASAL_8': {   'penalties_en': 'Administrative guidelines for destination management, human resources, '
                                              'and cultural promotion.',
                              'text_en': '(2) The Tourism Ecosystem as referred to in paragraph (1) is implemented at '
                                         'minimum through: a. Tourism development planning; b. enhancement of Tourism '
                                         'Human Resources quality and Tourism education; c. Tourism Destination '
                                         'management; d. strengthening of the Tourism Industry; e. development of '
                                         'Tourism Attractions; f. provision of infrastructure and facilities; g. '
                                         'development of Tourism marketing; h. utilization of information and '
                                         'communication technology; i. empowerment of local communities; j. engagement '
                                         'of Tourism associations; k. strengthening of culture-based Tourism '
                                         'promotion; and/or l. organization of creative events.',
                              'title_en': 'Tourism Ecosystem Components & Implementation Standards (Article 8 '
                                          'Paragraph 2)',
                              'translation_status': 'ai-assisted'},
    'UU_22_2009_PASAL_291': {   'penalties_en': 'Imprisonment for a maximum of 1 (one) month or a maximum fine of '
                                                'Rp250.000,00 (two hundred fifty thousand rupiah).',
                                'text_en': 'Pasal 106\n'
                                           '(8) Every person who drives a Motorcycle and Motorcycle Passengers are '
                                           'required to wear a helmet that meets Indonesian national standards.\n'
                                           '\n'
                                           'Pasal 291\n'
                                           '(1) Every person who drives a Motorcycle without wearing a helmet that '
                                           'meets Indonesian national standards as referred to in Pasal 106 paragraph '
                                           '(8) shall be punished with imprisonment for a maximum of 1 (one) month or '
                                           'a fine of at most Rp250.000,00 (two hundred fifty thousand rupiah).\n'
                                           '(2) Every person who drives a Motorcycle and allows passenger(s) not to '
                                           'wear a helmet as referred to in Pasal 106 paragraph (8) shall be punished '
                                           'with imprisonment for a maximum of 1 (one) month or a fine of at most '
                                           'Rp250.000,00 (two hundred fifty thousand rupiah).',
                                'title_en': 'Mandatory Standard Helmet for Motorcycle Riders (Articles 106 & 291)',
                                'translation_status': 'ai-assisted'},
    'UU_22_2009_PASAL_77_281': {   'penalties_en': 'Imprisonment for a maximum of 4 (four) months or a maximum fine of '
                                                   'Rp1.000.000,00 (one million rupiah).',
                                   'text_en': 'Pasal 77\n'
                                              '(1) Every person who drives a Motor Vehicle on the Road is required to '
                                              'have a Driving License (Surat Izin Mengemudi - SIM) corresponding to '
                                              'the type of Motor Vehicle being driven.\n'
                                              '\n'
                                              'Pasal 281\n'
                                              'Every person who drives a Motor Vehicle on the Road without having a '
                                              'Driving License (Surat Izin Mengemudi - SIM) as referred to in Pasal 77 '
                                              'paragraph (1) shall be punished with imprisonment for a maximum of 4 '
                                              '(four) months or a fine of at most Rp1.000.000,00 (one million rupiah).',
                                   'title_en': 'Mandatory Driving License (SIM) for Motor Vehicles (Articles 77 & 281)',
                                   'translation_status': 'ai-assisted'},
    'UU_39_1999_PASAL_1_3': {   'penalties_en': 'Actionable violation under National Human Rights Commission (Komnas '
                                                'HAM) statutory mechanisms.',
                                'text_en': 'Discrimination is any restriction, harassment, or ostracism, whether '
                                           'direct or indirect, grounded in distinction among human beings on the '
                                           'basis of religion, ethnicity, race, group, class, social status, economic '
                                           'status, gender, language, or political conviction, which results in the '
                                           'impairment, diversion, or nullification of the recognition, exercise, or '
                                           'enjoyment of human rights and fundamental freedoms in life, whether '
                                           'individually or collectively, in the political, economic, legal, social, '
                                           'cultural, and other spheres of life.',
                                'title_en': 'Statutory Definition of Human Rights Discrimination',
                                'translation_status': 'ai-assisted'},
    'UU_40_2008_PASAL_1': {   'penalties_en': 'Statutory legal basis defining discriminatory acts subject to civil '
                                              'action, human rights intervention, and criminal penalties under this '
                                              'Law.',
                              'text_en': 'Racial and ethnic discrimination is any distinction, exclusion, restriction, '
                                         'or preference based on race and ethnicity that has the purpose or effect of '
                                         'nullifying or impairing the recognition, enjoyment, or exercise, on an equal '
                                         'footing, of human rights and fundamental freedoms in the civil, political, '
                                         'economic, social, and cultural fields.',
                              'title_en': 'Statutory Definition of Racial & Ethnic Discrimination',
                              'translation_status': 'ai-assisted'},
    'UU_40_2008_PASAL_15': {   'penalties_en': 'Imprisonment for a maximum of 1 year and/or maximum fine of '
                                               'Rp100,000,000.',
                               'text_en': 'Every person who intentionally conducts distinction, exclusion, '
                                          'restriction, or preference based on race and ethnicity resulting in '
                                          'revocation or impairment of recognition, enjoyment, or exercise of human '
                                          'rights and fundamental freedoms on equal terms in civil, political, '
                                          'economic, social, and cultural fields as referred to in Pasal 4 letter a, '
                                          'shall be sentenced to imprisonment for a maximum of 1 (satu) year and/or a '
                                          'maximum fine of Rp100.000.000,00 (seratus juta rupiah).',
                               'title_en': 'Criminal Sanction for Racial/Ethnic Discrimination',
                               'translation_status': 'ai-assisted'},
    'UU_40_2008_PASAL_16_17': {   'penalties_en': 'Imprisonment up to 5 years and/or fine up to Rp500,000,000; violent '
                                                  'crimes incur sentence enhanced by one-third (1/3).',
                                  'text_en': 'Pasal 16: Every person who intentionally demonstrates hatred or '
                                             'animosity toward others based on racial and ethnic discrimination as '
                                             'referred to in Pasal 4 letter b point 1, point 2, or point 3, shall be '
                                             'sentenced to imprisonment for a maximum of 5 (lima) years and/or a '
                                             'maximum fine of Rp500.000.000,00 (lima ratus juta rupiah). Pasal 17: '
                                             'Every person who intentionally commits deprivation of life, assault, '
                                             'rape, lewd acts, robbery with violence, or deprivation of liberty '
                                             'grounded in racial and ethnic discrimination as referred to in Pasal 4 '
                                             'letter b point 4, shall be penalized in accordance with statutory penal '
                                             'provisions with an additional 1/3 (sepertiga) added to respective '
                                             'maximum statutory penalties.',
                                  'title_en': 'Criminal Penalties for Public Hate Propaganda & Violent Discrimination',
                                  'translation_status': 'ai-assisted'},
    'UU_40_2008_PASAL_4': {   'penalties_en': 'Subject to criminal sanctions of 1 to 5 years imprisonment and heavy '
                                              'fines under Articles 15 to 17 of this Law.',
                              'text_en': 'Racial and ethnic discriminatory acts include: a. applying distinction, '
                                         'exclusion, restriction, or preference based on race and ethnicity that '
                                         'results in revocation or impairment of the recognition, enjoyment, or '
                                         'exercise of human rights and fundamental freedoms on equal terms in civil, '
                                         'political, economic, social, and cultural fields; or b. manifesting hatred '
                                         'or feelings of enmity toward persons due to racial and ethnic differences '
                                         'through acts of: 1. making writings or images to be placed, affixed, or '
                                         'disseminated in public places or other venues visible or legible to others; '
                                         '2. delivering speeches, expressing, or uttering specific statements in '
                                         'public places or other venues audible to others; 3. wearing or displaying '
                                         "objects, words, or images on one's person in public places or other venues "
                                         'legible to others; or 4. committing deprivation of life, assault, rape, lewd '
                                         'acts, robbery with violence, or deprivation of liberty grounded in racial '
                                         'and ethnic discrimination.',
                              'title_en': 'Prohibited Discriminatory Acts & Public Hate Expressions',
                              'translation_status': 'ai-assisted'}}

