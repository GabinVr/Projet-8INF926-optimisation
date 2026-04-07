{

inputs = {
  # nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  nixpkgs.url = "github:SkohTV/nixpkgs/init-nomad-gerad";
};

outputs = { self, nixpkgs }:

let
  supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
  forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
  nixpkgsFor = forAllSystems (system: import nixpkgs { inherit system; });

in {

  # `nix develop`
  devShells = forAllSystems (system: {
    default = nixpkgsFor.${system}.mkShell {
      buildInputs = with nixpkgsFor.${system}; [
        nomad-gerad
        julia
        (python3.withPackages (ps: [ ps.pandas ]))
      ];
    };
  });

};

}
