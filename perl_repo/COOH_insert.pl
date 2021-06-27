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
    $doc->Export("Au_s0_COOH/${output}_COOH.msi");
    $doc->Discard;
    $doc->Close;
}
