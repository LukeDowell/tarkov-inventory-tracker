export type HelmetArea = "Top" | "Nape" | "Ears" | "Eyes" | "Jaws"

export type RicochetChance = "None" | "Low" | "Medium" | "High"

export type SoundReduction = "None" | "Low" | "High"

export type ArmorMaterial = "Combined materials" | "Aramid" | "Armor steel" | "UHMWPE" | "Aluminium" | "Titan"

export type ArmorClass = 1 | 2 | 3 | 4 | 5 | 6

export interface Helmet {
  name: string,
  material: ArmorMaterial,
  class: ArmorClass,
  areas: HelmetArea[],
  durability: number,
  effectiveDurability: number,
  ricochetChance: RicochetChance,
  movementSpeedPenalty: number,
  turningSpeedPenalty: number,
  ergonomicsPenalty: number,
  soundReductionPenalty: SoundReduction,
  blocksHeadset: boolean,
  weight: number
}
