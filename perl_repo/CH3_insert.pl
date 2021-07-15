foreach my $item (@params) {
    my $source = $item->[0];
    my $C_x    = $item->[1];
    my $C_y    = $item->[2];
    my $C_z    = $item->[3];
    my $H1_x    = $item->[4];
    my $H1_y    = $item->[5];
    my $H1_z    = $item->[6];
    my $H2_x    = $item->[7];
    my $H2_y    = $item->[8];
    my $H2_z    = $item->[9];
    my $H3_x    = $item->[10];
    my $H3_y    = $item->[11];
    my $H3_z    = $item->[12];
    my $output = $item->[13];
    my $doc    = $Documents{"${source}"};
    my $C      = $doc->CreateAtom( "C",
        $doc->FromFractionalPosition( Point( X => $C_x, Y => $C_y, Z => $C_z ) ) );
    my $H1      = $doc->CreateAtom( "H",
        $doc->FromFractionalPosition( Point( X => $H1_x, Y => $H1_y, Z => $H1_z ) ) );
    my $H2      = $doc->CreateAtom( "H",
        $doc->FromFractionalPosition( Point( X => $H2_x, Y => $H2_y, Z => $H2_z ) ) );
    my $H3      = $doc->CreateAtom( "H",
        $doc->FromFractionalPosition( Point( X => $H3_x, Y => $H3_y, Z => $H3_z ) ) );
    $doc->CalculateBonds;
    $doc->Export("${output}_CH3.msi");
    $doc->Discard;
    $doc->Close;
}
