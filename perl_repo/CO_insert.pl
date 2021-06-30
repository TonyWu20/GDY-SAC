foreach my $item (@params) {
    my $source = $item->[0];
    my $C_x    = $item->[1];
    my $C_y    = $item->[2];
    my $C_z    = $item->[3];
    my $O_x    = $item->[4];
    my $O_y    = $item->[5];
    my $O_z    = $item->[6];
    my $output = $item->[7];
    my $doc    = $Documents{"${source}"};
    my $C      = $doc->CreateAtom( "C",
        $doc->FromFractionalPosition( Point( X => $C_x, Y => $C_y, Z => $C_z ) ) );
    my $O = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O_x, Y => $O_y, Z => $O_z ) ) );
    $doc->CalculateBonds;
    my $newDoc = $doc->Export("${output}_CO.msi");
    $doc->Discard;
    $doc->Close;
}
