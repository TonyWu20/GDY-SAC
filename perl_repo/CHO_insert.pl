foreach my $item (@params) {
    my $source = $item->[0];
    my $C_x    = $item->[1];
    my $C_y    = $item->[2];
    my $C_z    = $item->[3];
    my $O_x   = $item->[4];
    my $O_y   = $item->[5];
    my $O_z   = $item->[6];
    my $H_x   = $item->[7];
    my $H_y   = $item->[8];
    my $H_z   = $item->[9];
    my $output = $item->[10];
    my $doc    = $Documents{"${source}"};
    my $C      = $doc->CreateAtom( "C",
        $doc->FromFractionalPosition( Point( X => $C_x, Y => $C_y, Z => $C_z ) ) );
    my $O = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O_x, Y => $O_y, Z => $O_z ) ) );
    my $H = $doc->CreateAtom( "H",
        $doc->FromFractionalPosition( Point( X => $H_x, Y => $H_y, Z => $H_z ) ) );
    $doc->CalculateBonds;
    $doc->Export("Au_s0_CHO/${output}_CHO.msi");
    $doc->Discard;
    $doc->Close;
}
