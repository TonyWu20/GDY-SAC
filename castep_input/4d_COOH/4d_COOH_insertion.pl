#!perl
use strict;
use Getopt::Long;
use MaterialsScript qw(:all);
my @params = (
	['../GDY_SAC_models/4d/SAC_GDY_Ag.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Ag'],
	['../GDY_SAC_models/4d/SAC_GDY_Cd.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Cd'],
	['../GDY_SAC_models/4d/SAC_GDY_Mo.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Mo'],
	['../GDY_SAC_models/4d/SAC_GDY_Nb.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Nb'],
	['../GDY_SAC_models/4d/SAC_GDY_Pd.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Pd'],
	['../GDY_SAC_models/4d/SAC_GDY_Rh.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Rh'],
	['../GDY_SAC_models/4d/SAC_GDY_Ru.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Ru'],
	['../GDY_SAC_models/4d/SAC_GDY_Tc.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Tc'],
	['../GDY_SAC_models/4d/SAC_GDY_Y.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Y'],
	['../GDY_SAC_models/4d/SAC_GDY_Zr.xsd',  0.393484, 0.60653, 0.641022, 0.452616, 0.654064, 0.702953, 0.324733, 0.551265, 0.702953, 0.283777, 0.518343, 0.636375, 'SAC_GDY_Zr'],
);
foreach my $item (@params) {
    my $source = $item->[0];
    my $C_x    = $item->[1];
    my $C_y    = $item->[2];
    my $C_z    = $item->[3];
    my $O1_x   = $item->[4];
    my $O1_y   = $item->[5];
    my $O1_z   = $item->[6];
    my $O2_x   = $item->[7];
    my $O2_y   = $item->[8];
    my $O2_z   = $item->[9];
    my $H_x    = $item->[10];
    my $H_y    = $item->[11];
    my $H_z    = $item->[12];
    my $output = $item->[13];
    my $doc    = $Documents{"${source}"};
    my $C      = $doc->CreateAtom( "C",
        $doc->FromFractionalPosition( Point( X => $C_x, Y => $C_y, Z => $C_z ) ) );
    my $O1 = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O1_x, Y => $O1_y, Z => $O1_z ) ) );
    my $O2 = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O2_x, Y => $O2_y, Z => $O2_z ) ) );
    my $H = $doc->CreateAtom( "H", $doc->FromFractionalPosition( Point( X => $H_x, Y=> $H_y, Z => $H_z ) ) );
    $doc->CalculateBonds;
    $doc->Export("${output}_COOH.msi");
    $doc->Discard;
    $doc->Close;
}
