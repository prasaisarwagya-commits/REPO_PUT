"""
Dungeon Battle - a simple turn-based game showing Python OOP.

Concepts used:
- Classes and objects
- Inheritance (Player and Enemy extend Character)
- Encapsulation (each class manages its own data)
- Polymorphism (Enemy overrides choose_action)
Run with:  python dungeon_battle.py
"""

import random


class Character:
    """Base class for anything that can fight."""

    def __init__(self, name, max_hp, attack, defense):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        damage = max(1, amount - self.defense)
        self.hp = max(0, self.hp - damage)
        return damage

    def attack_target(self, target):
        roll = random.randint(self.attack - 2, self.attack + 2)
        return target.take_damage(roll)

    def health_bar(self, length=20):
        filled = int(length * self.hp / self.max_hp)
        return f"[{'#' * filled}{'-' * (length - filled)}] {self.hp}/{self.max_hp}"

    def __str__(self):
        return f"{self.name} {self.health_bar()}"


class Player(Character):
    """The hero controlled by the user."""

    def __init__(self, name):
        super().__init__(name, max_hp=50, attack=8, defense=2)
        self.potions = 3
        self.level = 1
        self.xp = 0
        self.xp_needed = 20

    def heavy_attack(self, target):
        """Risky move: 60% chance to hit for double damage, otherwise miss."""
        if random.random() < 0.6:
            roll = random.randint(self.attack - 2, self.attack + 2) * 2
            return target.take_damage(roll)
        return 0

    def use_potion(self):
        if self.potions <= 0:
            return None
        self.potions -= 1
        healed = min(20, self.max_hp - self.hp)
        self.hp += healed
        return healed

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level_up()
            leveled = True
        return leveled

    def level_up(self):
        self.level += 1
        self.xp_needed = int(self.xp_needed * 1.5)
        self.max_hp += 10
        self.attack += 2
        self.defense += 1
        self.hp = self.max_hp
        print(f"\n*** LEVEL UP! You are now level {self.level}. HP, attack and defense increased! ***")

    def __str__(self):
        return f"{self.name} (Lv {self.level}) {self.health_bar()}  Potions: {self.potions}"


class Enemy(Character):
    """A monster. Overrides choose_action to show polymorphism."""

    def __init__(self, name, max_hp, attack, defense, xp_reward):
        super().__init__(name, max_hp, attack, defense)
        self.xp_reward = xp_reward

    def choose_action(self):
        # 20% of the time the enemy goes for a powerful strike
        return "power" if random.random() < 0.2 else "normal"

    def take_turn(self, target):
        if self.choose_action() == "power":
            roll = random.randint(self.attack - 1, self.attack + 3) * 2
            damage = target.take_damage(roll)
            print(f"{self.name} unleashes a POWER STRIKE for {damage} damage!")
        else:
            damage = self.attack_target(target)
            print(f"{self.name} hits you for {damage} damage.")


class Boss(Enemy):
    """A tougher enemy that also regenerates a little each turn."""

    def take_turn(self, target):
        regen = min(3, self.max_hp - self.hp)
        self.hp += regen
        if regen:
            print(f"{self.name} regenerates {regen} HP.")
        super().take_turn(target)


class Game:
    """Controls the game loop."""

    ENEMY_TEMPLATES = [
        ("Goblin", 20, 5, 0, 10),
        ("Skeleton", 28, 7, 1, 14),
        ("Orc", 38, 9, 2, 20),
        ("Dark Mage", 32, 12, 1, 24),
    ]

    def __init__(self):
        self.player = None
        self.battles_won = 0

    def create_enemy(self):
        # Every 5th battle is a boss fight
        if (self.battles_won + 1) % 5 == 0:
            scale = 1 + self.battles_won * 0.1
            return Boss("Dragon Lord", int(80 * scale), int(14 * scale), 3, 60)
        name, hp, atk, df, xp = random.choice(self.ENEMY_TEMPLATES)
        scale = 1 + self.battles_won * 0.15
        return Enemy(name, int(hp * scale), int(atk * scale), df, xp)

    def show_status(self, enemy):
        print("\n" + "-" * 50)
        print(self.player)
        print(enemy)
        print("-" * 50)

    def player_turn(self, enemy):
        """Returns True if the player escaped."""
        while True:
            print("1) Attack   2) Heavy attack (60% hit, 2x dmg)   3) Potion   4) Run")
            choice = input("Choose: ").strip()
            if choice == "1":
                dmg = self.player.attack_target(enemy)
                print(f"You hit {enemy.name} for {dmg} damage.")
                return False
            if choice == "2":
                dmg = self.player.heavy_attack(enemy)
                if dmg:
                    print(f"CRUSHING BLOW! {dmg} damage to {enemy.name}.")
                else:
                    print("You swing wildly and miss!")
                return False
            if choice == "3":
                healed = self.player.use_potion()
                if healed is None:
                    print("You have no potions left! Pick another action.")
                    continue
                print(f"You drink a potion and restore {healed} HP.")
                return False
            if choice == "4":
                if random.random() < 0.5:
                    print("You escaped!")
                    return True
                print("You failed to escape!")
                return False
            print("Invalid choice, try again.")

    def battle(self, enemy):
        print(f"\nA wild {enemy.name} appears!")
        while self.player.is_alive() and enemy.is_alive():
            self.show_status(enemy)
            escaped = self.player_turn(enemy)
            if escaped:
                return "escaped"
            if not enemy.is_alive():
                break
            enemy.take_turn(self.player)
        return "won" if self.player.is_alive() else "lost"

    def reward(self, enemy):
        print(f"\nYou defeated {enemy.name}! +{enemy.xp_reward} XP")
        self.player.gain_xp(enemy.xp_reward)
        if random.random() < 0.4:
            self.player.potions += 1
            print("The enemy dropped a potion!")

    def run(self):
        print("=" * 50)
        print("        WELCOME TO DUNGEON BATTLE")
        print("=" * 50)
        name = input("Enter your hero's name: ").strip() or "Hero"
        self.player = Player(name)

        while self.player.is_alive():
            enemy = self.create_enemy()
            result = self.battle(enemy)

            if result == "won":
                self.battles_won += 1
                self.reward(enemy)
            elif result == "lost":
                break

            again = input("\nContinue deeper into the dungeon? (y/n): ").strip().lower()
            if again != "y":
                break

        print("\n" + "=" * 50)
        if self.player.is_alive():
            print(f"You left the dungeon alive with {self.battles_won} victories. Well done!")
        else:
            print(f"You were defeated after {self.battles_won} victories. Game over.")
        print("=" * 50)


if __name__ == "__main__":
    Game().run()