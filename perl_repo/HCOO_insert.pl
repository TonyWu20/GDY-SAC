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
    my $H1_x    = $item->[10];
    my $H1_y    = $item->[11];
    my $H1_z    = $item->[12];
    my $output = $item->[13];
    my $doc    = $Documents{"${source}"};
    my $C      = $doc->CreateAtom( "C",
        $doc->FromFractionalPosition( Point( X => $C_x, Y => $C_y, Z => $C_z ) ) );
    my $O1 = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O1_x, Y => $O1_y, Z => $O1_z ) ) );
    my $O2 = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O2_x, Y => $O2_y, Z => $O2_z ) ) );
    my $H1 = $doc->CreateAtom( "H", $doc->FromFractionalPosition( Point( X => $H1_x, Y=> $H1_y, Z => $H1_z ) ) );
    $doc->CalculateBonds;
    $doc->Export("${output}_HCOO.msi");
    $doc->Discard;
    $doc->Close;
}
