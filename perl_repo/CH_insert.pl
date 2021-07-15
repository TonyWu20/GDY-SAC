foreach my $item (@params) {
    my $source = $item->[0];
    my $C_x    = $item->[1];
    my $C_y    = $item->[2];
    my $C_z    = $item->[3];
    my $H1_x    = $item->[4];
    my $H1_y    = $item->[5];
    my $H1_z    = $item->[6];
    my $output = $item->[7];
    my $doc    = $Documents{"${source}"};
    my $C      = $doc->CreateAtom( "C",
        $doc->FromFractionalPosition( Point( X => $C_x, Y => $C_y, Z => $C_z ) ) );
    my $H1      = $doc->CreateAtom( "H",
        $doc->FromFractionalPosition( Point( X => $H1_x, Y => $H1_y, Z => $H1_z ) ) );
    $doc->CalculateBonds;
    $doc->Export("${output}_CH.msi");
    $doc->Discard;
    $doc->Close;
}
