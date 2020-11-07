# 开发工具
server : python，用vs code开发

client : C#，用vs开发

# 数值体系
- 总内容
  - 要体现各种族之间的差异
  - 要体现同一种族不同个体在战斗经验和能力水平上的差距
  - 能力平庸但掌握特殊技能的个体，在战场上应该有表现自己的机会
  - 强大的个体使用斗气，魔化或变身等方式，可以在短时间极大地强化自己的能力
  - 要充分考虑到武器和技能威力的影响
- 能力值
  - 种族值RACE
    - HP∈[1, 256]∩N
    - STR∈[1, 256]∩N
    - DEF∈[1, 256]∩N
    - ATS∈[1, 256]∩N
    - ADF∈[1, 256]∩N
    - SPD∈[1, 256]∩N
  - 个体值IND∈{-6%, -4%, -2%, 0%, 2%, 4%, 6%}
  - 努力值EFO∈[0, 63]∩N
  - 性格值∈{0.9, 1, 1.1}
  - 等级LEVEL∈[1, 100]
  - 满级能力值
    - ABLILITY<sub>std</sub>=(RACE·2·(1+IND)+EFO)·性格值
    - HP<sub>std</sub>=RACE·2·(1+IND)+EFO
    - MP<sub>std</sub>=960
  - 裸装能力值
    - ABLILITY<sub>no_equip</sub>= ABLILITY<sub>std</sub>·(0.05+LEVEL/LEVEL<sup>max</sup>)·5
    - HP<sub>no_equip</sub>== HP<sub>std</sub> ·(1+LEVEL/LEVEL<sup>max</sup>)·48
    - 参考值为IND和EFO均为0的函数值
    - MP<sub>no_equip</sub>==960
  - ABILITY<sub>real</sub>= ABLILITY<sub>no_equip</sub>·RATE<sub>ability</sub>+BONUS<sub>ability</sub>
    - RATE<sub>ability</sub>和BONUS<sub>ability</sub>来源于装备特效、被动技能以及战斗中的各种效果和环境影响
    - 口袋妖怪的“系”相当于一些被动技能效果的组合，提升特定属性的攻击力，影响很多属性的防御力。对每个系，都有STR/DEF/ATS/ADF四个能力值
    - 对有些技能，武器直接影响技能威力，高级武器还可以提升人物特定类型的攻击能力值
- 技能
  - ID、名称、介绍、FLAG
  - 场地法术/直接攻击
  - 射程、半径、角度、敌我识别
  - 系、物魔类型
  - 特效组
    - 特效具有POWER, RATE, TIME, IS_DAMAGE
    - 各类伤害和其它特效的地位等同，但是有IS_DAMAGE属性作为区别
    - 对所有伤害类型的特效，POWER<sub>real</sub>=POWER<sub>std</sub>·RATE<sub>power</sub>
    - RATE<sub>power</sub>来源于装备特效、被动技能以及战斗中的各种效果和环境影响
- 伤害
  - Damage=攻击方STR<sub>real</sub>/防御方DEF<sub>real</sub>·POWER<sub>real</sub>·RATE<sub>environment</sub>
  - RATE<sub>environment</sub>的典型例子：多重鳞片、大晴天、光之壁、用地震攻击正在挖洞的对手
