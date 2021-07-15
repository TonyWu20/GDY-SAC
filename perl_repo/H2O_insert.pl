foreach my $item (@params) {
    my $source = $item->[0];
    my $O_x    = $item->[1];
    my $O_y    = $item->[2];
    my $O_z    = $item->[3];
    my $H1_x   = $item->[4];
    my $H1_y   = $item->[5];
    my $H1_z   = $item->[6];
    my $H2_x   = $item->[7];
    my $H2_y   = $item->[8];
    my $H2_z   = $item->[9];
    my $output = $item->[10];
    my $doc    = $Documents{"${source}"};
    my $O      = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O_x Y => $O_y, Z => $O_z ) ) );
    my $H1 = $doc->CreateAtom( "H",
        $doc->FromFractionalPosition( Point( X => $H1_x, Y => $H1_y, Z => $H1_z ) ) );
    my $H2 = $doc->CreateAtom( "H",
        $doc->FromFractionalPosition( Point( X => $H2_x, Y => $H2_y, Z => $H2_z ) ) );
    $doc->CalculateBonds;
    $doc->Export("${output}_H2O.msi");
    $doc->Discard;
    $doc->Close;
}
