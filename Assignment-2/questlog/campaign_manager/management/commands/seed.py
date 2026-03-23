"""
Management command: python manage.py seed

Populates the database with sample data so the app feels alive right away.
This command is safe to run multiple times — it uses get_or_create() throughout,
so existing records are skipped rather than duplicated.

Usage:
    python manage.py seed
"""

import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from campaign_manager.models import (
    Campaign, CampaignPlayer, Character,
    Item, CharacterItem, Session, Encounter, Spell, CharacterSpell, PreparedSpell
)


class Command(BaseCommand):
    help = 'Seeds the database with sample campaigns, characters, sessions, and items.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n⚔  QuestLog — Seeding database...\n'))

        # ── Users ────────────────────────────────────────────────────────
        self.stdout.write('Creating users...')

        dm, dm_created = User.objects.get_or_create(username='dungeon_master')
        if dm_created:
            dm.set_password('password123')
            dm.first_name = 'Gandalf'
            dm.last_name  = 'Grey'
            dm.save()

        p1, p1_created = User.objects.get_or_create(username='player_one')
        if p1_created:
            p1.set_password('password123')
            p1.first_name = 'Thorin'
            p1.save()

        p2, p2_created = User.objects.get_or_create(username='player_two')
        if p2_created:
            p2.set_password('password123')
            p2.first_name = 'Arwen'
            p2.save()

        # Superuser for the Django admin panel
        admin_user, admin_created = User.objects.get_or_create(username='admin')
        if admin_created:
            admin_user.set_password('admin123')
            admin_user.is_staff     = True
            admin_user.is_superuser = True
            admin_user.save()

        # ── Campaigns ────────────────────────────────────────────────────
        self.stdout.write('Creating campaigns...')

        campaign1, _ = Campaign.objects.get_or_create(
            name='The Lost Mines of Phandelver',
            defaults={
                'description': (
                    "A classic adventure for beginning characters. The party has been hired to "
                    "escort a wagon of supplies to the frontier town of Phandalin, but things go "
                    "sideways almost immediately when they discover their contact has gone missing."
                ),
                'world_name':      'Faerûn',
                'status':          'active',
                'dungeon_master':  dm,
            },
        )

        campaign2, _ = Campaign.objects.get_or_create(
            name='Curse of Strahd',
            defaults={
                'description': (
                    "The party is drawn into the dark land of Barovia, ruled by the vampire "
                    "Strahd von Zarovich. Surrounded by mists and dread, they must find a way "
                    "to defeat the Count before he destroys them — or worse, makes them stay forever."
                ),
                'world_name':     'Barovia',
                'status':         'on_hold',
                'dungeon_master': dm,
            },
        )

        # ── Campaign membership ──────────────────────────────────────────
        self.stdout.write('Creating campaign memberships...')

        # Campaign 1 members
        CampaignPlayer.objects.get_or_create(campaign=campaign1, user=dm, defaults={'role': 'dm'})
        CampaignPlayer.objects.get_or_create(campaign=campaign1, user=p1, defaults={'role': 'player'})
        CampaignPlayer.objects.get_or_create(campaign=campaign1, user=p2, defaults={'role': 'player'})

        # Campaign 2 members
        CampaignPlayer.objects.get_or_create(campaign=campaign2, user=dm, defaults={'role': 'dm'})
        CampaignPlayer.objects.get_or_create(campaign=campaign2, user=p1, defaults={'role': 'player'})
        CampaignPlayer.objects.get_or_create(campaign=campaign2, user=p2, defaults={'role': 'player'})

        # ── Characters ───────────────────────────────────────────────────
        self.stdout.write('Creating characters...')

        thorin, _ = Character.objects.get_or_create(
            name='Thorin Ironforge',
            campaign=campaign1,
            defaults={
                'race':             'dwarf',
                'character_class':  'fighter',
                'level':            3,
                'hit_points':       28,
                'background_story': (
                    "A veteran soldier cast out from his clan after a failed siege. "
                    "Thorin now seeks glory — and a way to reclaim his family's honour."
                ),
                'player': p1,
            },
        )

        aria, _ = Character.objects.get_or_create(
            name='Aria Windwhisper',
            campaign=campaign1,
            defaults={
                'race':             'elf',
                'character_class':  'wizard',
                'level':            3,
                'hit_points':       16,
                'background_story': (
                    "A scholar of the arcane arts who left the great library of Silverymoon "
                    "to find a legendary tome rumoured to be hidden in the Sword Mountains."
                ),
                'player': p2,
            },
        )

        brand, _ = Character.objects.get_or_create(
            name='Brand Fairweather',
            campaign=campaign1,
            defaults={
                'race':             'human',
                'character_class':  'rogue',
                'level':            3,
                'hit_points':       18,
                'background_story': (
                    "A charming con-artist who grew up on the streets of Neverwinter. "
                    "Brand joined this expedition because the pay was good — and he had "
                    "to leave the city in a hurry anyway."
                ),
                'player': dm,  # The DM is also playing a character in this campaign
            },
        )

        viktor, _ = Character.objects.get_or_create(
            name='Viktor Draakholm',
            campaign=campaign2,
            defaults={
                'race':             'human',
                'character_class':  'paladin',
                'level':            5,
                'hit_points':       45,
                'background_story': (
                    "A paladin of the Morninglord who volunteered to investigate reports of "
                    "undead activity near the Svalich Woods. He did not expect to find himself "
                    "trapped in Barovia."
                ),
                'player': p1,
            },
        )

        sylva, _ = Character.objects.get_or_create(
            name='Sylva Moonpetal',
            campaign=campaign2,
            defaults={
                'race':             'elf',
                'character_class':  'druid',
                'level':            5,
                'hit_points':       32,
                'background_story': (
                    "A druid who sensed a deep wrongness in the natural world emanating from "
                    "the east. Following the sensation led her to the mists — and no exit."
                ),
                'player': p2,
            },
        )

        # ── Items ────────────────────────────────────────────────────────
        self.stdout.write('Creating items...')

        longsword, _ = Item.objects.get_or_create(
            name='Longsword',
            defaults={
                'description': 'A versatile one- or two-handed sword. Standard military issue.',
                'item_type':   'weapon',
                'rarity':      'common',
                'weight':      3.0,
                'value_gold':  15,
            },
        )

        chain_mail, _ = Item.objects.get_or_create(
            name='Chain Mail',
            defaults={
                'description': 'Interlocking metal rings providing solid protection. Heavy and noisy.',
                'item_type':   'armor',
                'rarity':      'common',
                'weight':      55.0,
                'value_gold':  75,
            },
        )

        health_potion, _ = Item.objects.get_or_create(
            name='Potion of Healing',
            defaults={
                'description': 'A bright red liquid that restores 2d4+2 hit points when consumed.',
                'item_type':   'potion',
                'rarity':      'common',
                'weight':      0.5,
                'value_gold':  50,
            },
        )

        spellbook, _ = Item.objects.get_or_create(
            name="Aria's Spellbook",
            defaults={
                'description': 'A worn leather tome filled with arcane formulae. Belongs to Aria.',
                'item_type':   'misc',
                'rarity':      'uncommon',
                'weight':      3.0,
                'value_gold':  50,
            },
        )

        shortsword, _ = Item.objects.get_or_create(
            name='Shortsword',
            defaults={
                'description': 'A light, quick blade suited for close quarters and finesse strikes.',
                'item_type':   'weapon',
                'rarity':      'common',
                'weight':      2.0,
                'value_gold':  10,
            },
        )

        cloak_elvenkind, _ = Item.objects.get_or_create(
            name='Cloak of Elvenkind',
            defaults={
                'description': (
                    "This gossamer cloak grants advantage on Dexterity (Stealth) checks "
                    "while the hood is up."
                ),
                'item_type':   'armor',
                'rarity':      'uncommon',
                'weight':      1.0,
                'value_gold':  0,  # Found, not bought
            },
        )

        staff_power, _ = Item.objects.get_or_create(
            name='Staff of Power',
            defaults={
                'description': (
                    "A powerful magical staff that holds 20 charges. It can be used to cast "
                    "several powerful spells and provides a +2 bonus to spell attack rolls."
                ),
                'item_type':   'weapon',
                'rarity':      'very_rare',
                'weight':      4.0,
                'value_gold':  0,  # Priceless
            },
        )

        holy_symbol, _ = Item.objects.get_or_create(
            name='Holy Symbol of Ravenkind',
            defaults={
                'description': (
                    "A sacred relic of Barovia. In the right hands, it can be used to repel "
                    "Strahd and his undead servants. One of the keys to breaking the curse."
                ),
                'item_type':   'quest',
                'rarity':      'legendary',
                'weight':      1.0,
                'value_gold':  0,
            },
        )

        # ── Inventory (CharacterItem join table) ──────────────────────────
        self.stdout.write('Assigning items to characters...')

        # Thorin's inventory
        CharacterItem.objects.get_or_create(
            character=thorin, item=longsword,
            defaults={'quantity': 1, 'equipped': True},
        )
        CharacterItem.objects.get_or_create(
            character=thorin, item=chain_mail,
            defaults={'quantity': 1, 'equipped': True},
        )
        CharacterItem.objects.get_or_create(
            character=thorin, item=health_potion,
            defaults={'quantity': 3, 'equipped': False},
        )

        # Aria's inventory
        CharacterItem.objects.get_or_create(
            character=aria, item=spellbook,
            defaults={'quantity': 1, 'equipped': True},
        )
        CharacterItem.objects.get_or_create(
            character=aria, item=health_potion,
            defaults={'quantity': 2, 'equipped': False},
        )
        CharacterItem.objects.get_or_create(
            character=aria, item=staff_power,
            defaults={'quantity': 1, 'equipped': True},
        )

        # Brand's inventory
        CharacterItem.objects.get_or_create(
            character=brand, item=shortsword,
            defaults={'quantity': 2, 'equipped': True},
        )
        CharacterItem.objects.get_or_create(
            character=brand, item=cloak_elvenkind,
            defaults={'quantity': 1, 'equipped': True},
        )
        CharacterItem.objects.get_or_create(
            character=brand, item=health_potion,
            defaults={'quantity': 1, 'equipped': False},
        )

        # Viktor's inventory
        CharacterItem.objects.get_or_create(
            character=viktor, item=longsword,
            defaults={'quantity': 1, 'equipped': True},
        )
        CharacterItem.objects.get_or_create(
            character=viktor, item=chain_mail,
            defaults={'quantity': 1, 'equipped': True},
        )
        CharacterItem.objects.get_or_create(
            character=viktor, item=health_potion,
            defaults={'quantity': 2, 'equipped': False},
        )

        # Sylva's inventory
        CharacterItem.objects.get_or_create(
            character=sylva, item=health_potion,
            defaults={'quantity': 2, 'equipped': False},
        )
        CharacterItem.objects.get_or_create(
            character=sylva, item=holy_symbol,
            defaults={'quantity': 1, 'equipped': True},
        )

        # ── Sessions ─────────────────────────────────────────────────────
        self.stdout.write('Creating sessions...')

        sess1c1, _ = Session.objects.get_or_create(
            campaign=campaign1, session_number=1,
            defaults={
                'date':           datetime.date(2024, 1, 15),
                'duration_hours': 3.5,
                'summary': (
                    "The party set out from Neverwinter with a wagon of goods bound for Phandalin. "
                    "On the Triboar Trail they were ambushed by goblins who had killed the horses "
                    "of their contact Gundren Rockseeker. Following the goblin trail, they cleared "
                    "a goblin hideout and rescued a wounded human named Sildar Hallwinter, who "
                    "told them Gundren had been taken to Cragmaw Castle."
                ),
            },
        )

        sess2c1, _ = Session.objects.get_or_create(
            campaign=campaign1, session_number=2,
            defaults={
                'date':           datetime.date(2024, 1, 29),
                'duration_hours': 4.0,
                'summary': (
                    "The party arrived in Phandalin with the wagon and learned the town is being "
                    "terrorised by a gang called the Redbrands, who work for a mysterious figure "
                    "known only as the Spider. The party made contact with townspeople and gathered "
                    "information about the Redbrand hideout beneath the Tresendar Manor ruins."
                ),
            },
        )

        sess3c1, _ = Session.objects.get_or_create(
            campaign=campaign1, session_number=3,
            defaults={
                'date':           datetime.date(2024, 2, 12),
                'duration_hours': 3.0,
                'summary': (
                    "The party infiltrated the Redbrand hideout. After dealing with a patrol and "
                    "navigating a treacherous underground passage over a chasm, they confronted "
                    "the Redbrands' leader — a renegade wizard named Iarno Albrek, alias 'Glasstaff'. "
                    "He attempted to flee but was captured. The hidden lair has been cleared."
                ),
            },
        )

        sess1c2, _ = Session.objects.get_or_create(
            campaign=campaign2, session_number=1,
            defaults={
                'date':           datetime.date(2024, 2, 5),
                'duration_hours': 4.5,
                'summary': (
                    "The mists closed around the party as they crossed an unmarked border. "
                    "They found themselves on the Svalich Road, unable to leave. Following the road, "
                    "they arrived at the village of Barovia, finding it shrouded in despair. A letter "
                    "written in the name of Strahd himself invited them to dine at Castle Ravenloft. "
                    "They wisely chose to explore the village and the old Death House instead."
                ),
            },
        )

        # ── Encounters ───────────────────────────────────────────────────
        self.stdout.write('Creating encounters...')

        # Session 1, Campaign 1
        Encounter.objects.get_or_create(
            session=sess1c1, name='Goblin Ambush',
            defaults={
                'description': (
                    "A band of eight goblins attacked from the roadside bushes. "
                    "Arrows flew before the party had a chance to draw weapons."
                ),
                'difficulty': 'easy',
                'outcome':    'victory',
            },
        )
        Encounter.objects.get_or_create(
            session=sess1c1, name='Klarg the Bugbear',
            defaults={
                'description': (
                    "The bugbear leader of the Cragmaw goblins, Klarg, guarded the inner cave "
                    "with his pet wolf Ripper. A tough fight in a smoke-filled chamber."
                ),
                'difficulty': 'hard',
                'outcome':    'victory',
            },
        )

        # Session 2, Campaign 1
        Encounter.objects.get_or_create(
            session=sess2c1, name='Redbrand Street Patrol',
            defaults={
                'description': (
                    "Four Redbrand ruffians accosted the party in the market square, "
                    "demanding they state their business and pay a 'toll'."
                ),
                'difficulty': 'medium',
                'outcome':    'fled',  # The party backed down to avoid causing a scene
            },
        )

        # Session 3, Campaign 1
        Encounter.objects.get_or_create(
            session=sess3c1, name="Glasstaff's Last Stand",
            defaults={
                'description': (
                    "The wizard Iarno Albrek attempted to fight his way out of his own sanctum, "
                    "hurling magic missiles and using a smokestick to cover his retreat. "
                    "Thorin tackled him before he reached the secret tunnel."
                ),
                'difficulty': 'deadly',
                'outcome':    'victory',
            },
        )
        Encounter.objects.get_or_create(
            session=sess3c1, name='Nothic in the Chasm',
            defaults={
                'description': (
                    "A nothic — a wizard transformed into a monster by dark magic — lurked "
                    "in a pit beneath the bridge over the cistern. It communicated telepathically, "
                    "revealing secrets about each party member before attacking."
                ),
                'difficulty': 'hard',
                'outcome':    'victory',
            },
        )

        # Session 1, Campaign 2
        Encounter.objects.get_or_create(
            session=sess1c2, name='The Death House',
            defaults={
                'description': (
                    "The party explored a haunted manor on the edge of Barovia village. "
                    "The house itself seemed alive, herding them deeper inside. They fled "
                    "before the monster in the basement could finish them off."
                ),
                'difficulty': 'hard',
                'outcome':    'fled',
            },
        )
        Encounter.objects.get_or_create(
            session=sess1c2, name="Strahd's Dinner Invitation",
            defaults={
                'description': (
                    "A coach bearing the crest of Castle Ravenloft arrived with a formal "
                    "invitation for dinner. The party negotiated the terms: they would attend, "
                    "but Strahd agreed not to feed on any of them that evening."
                ),
                'difficulty': 'medium',
                'outcome':    'negotiated',
            },
        )

        # ── Spells & Abilities ───────────────────────────────────────────────
        self.stdout.write('Creating spells and abilities...')

        # Classic Spells
        fireball, _ = Spell.objects.get_or_create(
            name="Fireball",
            defaults={
                "description": "A powerful explosion that deals massive area damage",
                "level_required": 5,
                "damage_effect": "8d6 fire damage (AoE)",
                "usage_limit": None,
                "type": "spell",
            }
        )

        magic_missile, _ = Spell.objects.get_or_create(
            name="Magic Missile",
            defaults={
                "description": "Automatically hits targets with glowing darts of force",
                "level_required": 1,
                "damage_effect": "3 darts, 1d4+1 each",
                "usage_limit": None,
                "type": "spell",
            }
        )

        cure_wounds, _ = Spell.objects.get_or_create(
            name="Cure Wounds",
            defaults={
                "description": "Restores hit points to a creature",
                "level_required": 1,
                "damage_effect": "Heals 1d8 + spellcasting modifier",
                "usage_limit": None,
                "type": "spell",
            }
        )

        shield, _ = Spell.objects.get_or_create(
            name="Shield",
            defaults={
                "description": "A quick magical barrier that boosts your defense",
                "level_required": 1,
                "damage_effect": "+5 AC until start of next turn",
                "usage_limit": None,
                "type": "spell",
            }
        )

        invisibility, _ = Spell.objects.get_or_create(
            name="Invisibility",
            defaults={
                "description": "Turns a creature unseen for stealth or escape",
                "level_required": 2,
                "damage_effect": "Creature becomes invisible",
                "usage_limit": None,
                "type": "spell",
            }
        )

        counterspell, _ = Spell.objects.get_or_create(
            name="Counterspell",
            defaults={
                "description": "Interrupts another spellcaster mid-cast",
                "level_required": 3,
                "damage_effect": "Automatically stops a spell of lower or equal level",
                "usage_limit": None,
                "type": "spell",
            }
        )

        fly, _ = Spell.objects.get_or_create(
            name="Fly",
            defaults={
                "description": "Grants the ability to soar through the air",
                "level_required": 3,
                "damage_effect": "Can fly at 60 ft speed",
                "usage_limit": None,
                "type": "spell",
            }
        )

        polymorph, _ = Spell.objects.get_or_create(
            name="Polymorph",
            defaults={
                "description": "Transforms a creature into another form",
                "level_required": 4,
                "damage_effect": "Changes target into beast form",
                "usage_limit": None,
                "type": "spell",
            }
        )

        # Combat-Oriented Spells
        eldritch_blast, _ = Spell.objects.get_or_create(
            name="Eldritch Blast",
            defaults={
                "description": "A staple ranged attack for warlocks",
                "level_required": 1,
                "damage_effect": "1d10 force damage",
                "usage_limit": None,
                "type": "spell",
            }
        )

        inflict_wounds, _ = Spell.objects.get_or_create(
            name="Inflict Wounds",
            defaults={
                "description": "Deals heavy necrotic damage through touch",
                "level_required": 1,
                "damage_effect": "3d10 necrotic damage",
                "usage_limit": None,
                "type": "spell",
            }
        )

        spiritual_weapon, _ = Spell.objects.get_or_create(
            name="Spiritual Weapon",
            defaults={
                "description": "Summons a floating weapon that attacks independently",
                "level_required": 2,
                "damage_effect": "1d8 + spellcasting modifier force damage per attack",
                "usage_limit": None,
                "type": "spell",
            }
        )

        hunters_mark, _ = Spell.objects.get_or_create(
            name="Hunter's Mark",
            defaults={
                "description": "Enhances damage against a chosen target",
                "level_required": 1,
                "damage_effect": "Extra 1d6 damage on attacks against marked target",
                "usage_limit": None,
                "type": "spell",
            }
        )

        guiding_bolt, _ = Spell.objects.get_or_create(
            name="Guiding Bolt",
            defaults={
                "description": "Radiant attack that grants advantage to the next hit",
                "level_required": 1,
                "damage_effect": "4d6 radiant damage and next attack has advantage",
                "usage_limit": None,
                "type": "spell",
            }
        )

        # Utility & Support Spells
        detect_magic, _ = Spell.objects.get_or_create(
            name="Detect Magic",
            defaults={
                "description": "Reveals magical auras nearby",
                "level_required": 1,
                "damage_effect": "Detect magical presence",
                "usage_limit": None,
                "type": "spell",
            }
        )

        identify, _ = Spell.objects.get_or_create(
            name="Identify",
            defaults={
                "description": "Learns properties of magical items",
                "level_required": 1,
                "damage_effect": "Reveals magical properties of one object",
                "usage_limit": None,
                "type": "spell",
            }
        )

        mage_hand, _ = Spell.objects.get_or_create(
            name="Mage Hand",
            defaults={
                "description": "Creates a spectral hand for interacting at a distance",
                "level_required": 1,
                "damage_effect": "Move/manipulate objects at 30 ft",
                "usage_limit": None,
                "type": "spell",
            }
        )

        leomunds_tiny_hut, _ = Spell.objects.get_or_create(
            name="Leomund's Tiny Hut",
            defaults={
                "description": "A protective dome for safe resting",
                "level_required": 3,
                "damage_effect": "Creates a dome that is impervious to external effects",
                "usage_limit": None,
                "type": "spell",
            }
        )

        feather_fall, _ = Spell.objects.get_or_create(
            name="Feather Fall",
            defaults={
                "description": "Slows descent to prevent fall damage",
                "level_required": 1,
                "damage_effect": "Reduces falling speed, no damage",
                "usage_limit": None,
                "type": "spell",
            }
        )

        # Class Abilities (Non-spell)
        rage, _ = Spell.objects.get_or_create(
            name="Rage",
            defaults={
                "description": "Boosts damage and resistance to harm",
                "level_required": 2,
                "damage_effect": "+2 melee damage, resistance to physical damage",
                "usage_limit": 3,
                "type": "ability",
            }
        )

        sneak_attack, _ = Spell.objects.get_or_create(
            name="Sneak Attack",
            defaults={
                "description": "Deals extra damage when attacking with advantage or positioning",
                "level_required": 1,
                "damage_effect": "1d6+1 per sneak attack dice",
                "usage_limit": None,
                "type": "ability",
            }
        )

        divine_smite, _ = Spell.objects.get_or_create(
            name="Divine Smite",
            defaults={
                "description": "Channels divine energy into weapon strikes",
                "level_required": 2,
                "damage_effect": "Adds 2d8 radiant damage on hit",
                "usage_limit": None,
                "type": "ability",
            }
        )

        wild_shape, _ = Spell.objects.get_or_create(
            name="Wild Shape",
            defaults={
                "description": "Transform into animals",
                "level_required": 2,
                "damage_effect": "Change form into selected beast",
                "usage_limit": None,
                "type": "ability",
            }
        )

        action_surge, _ = Spell.objects.get_or_create(
            name="Action Surge",
            defaults={
                "description": "Take an extra action in combat",
                "level_required": 2,
                "damage_effect": "Gain one extra action on your turn",
                "usage_limit": 1,
                "type": "ability",
            }
        )

        ki, _ = Spell.objects.get_or_create(
            name="Ki",
            defaults={
                "description": "Powers special techniques like Flurry of Blows",
                "level_required": 2,
                "damage_effect": "Use ki points for martial techniques",
                "usage_limit": None,
                "type": "ability",
            }
        )

        # High-Level / Iconic Spells
        wish, _ = Spell.objects.get_or_create(
            name="Wish",
            defaults={
                "description": "The most powerful spell, capable of altering reality",
                "level_required": 9,
                "damage_effect": "Alter reality per DM discretion",
                "usage_limit": 1,
                "type": "spell",
            }
        )

        meteor_swarm, _ = Spell.objects.get_or_create(
            name="Meteor Swarm",
            defaults={
                "description": "Calls down devastating meteors",
                "level_required": 9,
                "damage_effect": "20d6 fire + 20d6 bludgeoning damage",
                "usage_limit": None,
                "type": "spell",
            }
        )



        # ── Character Spells / Abilities (CharacterSpell join table) ─────────
        self.stdout.write('Assigning spells and abilities to characters...')

        # Thorin's spells/abilities
        CharacterSpell.objects.get_or_create(
            character=thorin, spell=fireball,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=thorin, spell=magic_missile,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=thorin, spell=shield,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=thorin, spell=rage,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=thorin, spell=action_surge,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=thorin, spell=wish,
            defaults={'prepared': False},  
        )
        CharacterSpell.objects.get_or_create(
            character=thorin, spell=meteor_swarm,
            defaults={'prepared': False},
        )

        # Aria's spells/abilities
        CharacterSpell.objects.get_or_create(
            character=aria, spell=magic_missile,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=aria, spell=cure_wounds,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=aria, spell=fireball,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=aria, spell=shield,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=aria, spell=mage_hand,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=aria, spell=leomunds_tiny_hut,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=aria, spell=wish,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=aria, spell=meteor_swarm,
            defaults={'prepared': False},
        )

        # Brand's spells/abilities
        CharacterSpell.objects.get_or_create(
            character=brand, spell=rage,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=brand, spell=sneak_attack,
            defaults={'prepared': True},
        )

        # Viktor's spells/abilities
        CharacterSpell.objects.get_or_create(
            character=viktor, spell=fireball,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=viktor, spell=magic_missile,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=viktor, spell=shield,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=viktor, spell=action_surge,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=viktor, spell=wish,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=viktor, spell=meteor_swarm,
            defaults={'prepared': False},
        )

        # Sylva's spells/abilities
        CharacterSpell.objects.get_or_create(
            character=sylva, spell=cure_wounds,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=sylva, spell=guiding_bolt,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=sylva, spell=spiritual_weapon,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=sylva, spell=detect_magic,
            defaults={'prepared': True},
        )
        CharacterSpell.objects.get_or_create(
            character=sylva, spell=identify,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=sylva, spell=wish,
            defaults={'prepared': False},
        )
        CharacterSpell.objects.get_or_create(
            character=sylva, spell=meteor_swarm,
            defaults={'prepared': False},
        )
        # ── Prepared Spells for Session ──────────────────────────────────
        # Aria's Prepared Spells 
        PreparedSpell.objects.get_or_create(
            character=aria, 
            spell= fireball,
            session=sess1c1,
            usage_remaining = -1,
        )
        PreparedSpell.objects.get_or_create(
            character=aria, 
            spell = magic_missile, 
            session=sess1c1, 
            usage_remaining=0, 
        )
        # Thorin's Prepared Spells 
        PreparedSpell.objects.get_or_create(
            character=thorin, 
            spell=rage, 
            session=sess1c1, 
            usage_remaining=2
        )
        PreparedSpell.objects.get_or_create(
            character=thorin,
            spell=shield,
            session=sess1c1,
            usage_remaining = -1
        )
        # Sylva's Prepared Spells
        PreparedSpell.objects.get_or_create(
            character=sylva,
            spell=cure_wounds,
            session=sess1c2,
            usage_remaining = -1
        )
        # Vicktor's Prepared Spells
        PreparedSpell.objects.get_or_create(
            character=viktor,
            spell=magic_missile,
            session=sess1c2,
            usage_remaining = -1
        )
        # ── Summary ──────────────────────────────────────────────────────
        self.stdout.write('\n' + '─' * 60)
        self.stdout.write(self.style.SUCCESS('✔  Seeding complete!\n'))
        self.stdout.write(self.style.MIGRATE_HEADING('Login credentials:'))
        self.stdout.write('  Regular users (password: password123)')
        self.stdout.write('    dungeon_master  — DM for both campaigns')
        self.stdout.write('    player_one      — plays Thorin & Viktor')
        self.stdout.write('    player_two      — plays Aria & Sylva')
        self.stdout.write('  Admin panel (password: admin123)')
        self.stdout.write('    admin           — visit /admin/ for the admin interface')
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('Database summary:'))
        self.stdout.write(f'  Users:          {User.objects.count()}')
        self.stdout.write(f'  Campaigns:      {Campaign.objects.count()}')
        self.stdout.write(f'  Members:        {CampaignPlayer.objects.count()}')
        self.stdout.write(f'  Characters:     {Character.objects.count()}')
        self.stdout.write(f'  Sessions:       {Session.objects.count()}')
        self.stdout.write(f'  Encounters:     {Encounter.objects.count()}')
        self.stdout.write(f'  Items:          {Item.objects.count()}')
        self.stdout.write(f'  Inventory rows: {CharacterItem.objects.count()}')
        self.stdout.write('')
        self.stdout.write('Run the server:  python manage.py runserver')
        self.stdout.write('Then visit:      http://127.0.0.1:8000/')
        self.stdout.write('─' * 60 + '\n')
        