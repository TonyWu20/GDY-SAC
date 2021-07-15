foreach my $item (@params) {
    my $source = $item->[0];
    my $O_x    = $item->[1];
    my $O_y    = $item->[2];
    my $O_z    = $item->[3];
    my $output = $item->[4];
    my $doc    = $Documents{"${source}"};
    my $O      = $doc->CreateAtom( "O",
        $doc->FromFractionalPosition( Point( X => $O_x, Y => $O_y, Z => $O_z ) ) );
    $doc->CalculateBonds;
    $doc->Export("${output}_O.msi");
    $doc->Discard;
    $doc->Close;
}
