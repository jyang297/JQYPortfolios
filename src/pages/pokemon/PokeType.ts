type Pokemon = {
  name: string;
  url: string;
};

export type PokemonRes = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Pokemon[];
};
