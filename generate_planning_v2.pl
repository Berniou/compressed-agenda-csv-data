#!/usr/bin/perl
use strict;
use warnings;
use utf8;

my @jours = qw(dimanche lundi mardi mercredi jeudi vendredi samedi);

mkdir "data" unless -d "data";

open(my $fh, '>:encoding(UTF-8)', 'data/planning_hebdo.csv') or die "Erreur ouverture: $!";
print $fh "heure," . join(",", @jours) . "\n";

my @preview = ();
my $line_count = 0;

for my $h (0..23) {
    for my $m (0, 15, 30, 45) {
        my $heure = sprintf("%02dh%02d", $h, $m);
        my $minute = $h * 60 + $m;
        my @vals = ($heure);

        for my $jour (@jours) {
            my $act = "Libre";

            # dimanche
            if ($jour eq "dimanche") {
                if ($minute >= 0 && $minute < 660) {
                    $act = "Sommeil";          # 00h-11h = 12h (partie 1)
                } elsif ($minute >= 660 && $minute < 690) {
                    $act = "Libre";            # 11h-11h30
                } elsif ($minute >= 690 && $minute < 930) {
                    $act = "Eglise";           # 11h30-15h30 = 4h
                } elsif ($minute >= 930 && $minute < 1020) {
                    $act = "Ménage";           # 15h30-17h = 1h30
                } elsif ($minute >= 1020 && $minute < 1110) {
                    $act = "Cuisine";          # 17h-18h30 = 1h30
                } elsif ($minute >= 1110 && $minute < 1170) {
                    $act = "Lessive";          # 18h30-19h30 = 1h
                } elsif ($minute >= 1170 && $minute < 1200) {
                    $act = "Libre";            # 19h30-20h = 30min
                } elsif ($minute >= 1200 && $minute < 1380) {
                    $act = "Famille";          # 20h-23h = 3h
                } elsif ($minute >= 1380 && $minute < 1440) {
                    $act = "Sommeil";          # 23h-00h = 1h (partie 2)
                }
            }
            # lundi : repos, FI, prière
            elsif ($jour eq "lundi") {
                if ($minute >= 0 && $minute < 390) {
                    $act = "Sommeil";          # 00h-06h30 = 6h30
                } elsif ($minute >= 390 && $minute < 450) {
                    $act = "Prière";           # 06h30-07h30 = 1h
                } elsif ($minute >= 450 && $minute < 570) {
                    $act = "FI";               # 07h30-09h30 = 2h
                } elsif ($minute >= 570 && $minute < 1350) {
                    $act = "Libre";            # 09h30-22h30 = 13h
                } elsif ($minute >= 1350 && $minute < 1440) {
                    $act = "Sommeil";          # 22h30-00h = 1h30
                }
            }
            # mardi / jeudi / samedi : travail + cuisine
            elsif ($jour =~ /^(mardi|jeudi|samedi)$/) {
                if (($minute >= 0 && $minute < 210) || ($minute >= 1170 && $minute < 1440)) {
                    $act = "Sommeil";          # 00h-03h30 + 19h30-00h = 8h
                } elsif ($minute >= 210 && $minute < 270) {
                    $act = "Prière";           # 03h30-04h30 = 1h
                } elsif ($minute >= 270 && $minute < 945) {
                    $act = "Travail";          # 04h30-15h45 = 11h15 (arrondi excès)
                } elsif ($minute >= 945 && $minute < 1005) {
                    $act = "Candidature";      # 15h45-16h45 = 1h
                } elsif ($minute >= 1005 && $minute < 1095) {
                    $act = "Cuisine";          # 16h45-18h15 = 1h30
                } elsif ($minute >= 1095 && $minute < 1170) {
                    $act = "Libre";            # 18h15-19h30 = 1h15
                }
            }
            # mercredi / vendredi : travail + ménage
            elsif ($jour =~ /^(mercredi|vendredi)$/) {
                if (($minute >= 0 && $minute < 210) || ($minute >= 1170 && $minute < 1440)) {
                    $act = "Sommeil";          # 8h
                } elsif ($minute >= 210 && $minute < 270) {
                    $act = "Prière";           # 1h
                } elsif ($minute >= 270 && $minute < 945) {
                    $act = "Travail";          # 11h15
                } elsif ($minute >= 945 && $minute < 1005) {
                    $act = "Candidature";      # 1h
                } elsif ($minute >= 1005 && $minute < 1095) {
                    $act = "Ménage";           # 1h30
                } elsif ($minute >= 1095 && $minute < 1170) {
                    $act = "Libre";            # 1h15
                }
            }

            push @vals, $act;
        }

        my $line = join(",", @vals) . "\n";
        print $fh $line;
        if ($line_count < 20) {
            push @preview, $line;
            $line_count++;
        }
    }
}

close($fh);

print "=== Apercu des 20 premieres lignes ===\n";
print @preview;
print "\nFichier genere : data/planning_hebdo.csv\n";

# Verification rapide des volumes
print "\n=== Volumes hebdomadaires (en heures) ===\n";
open(my $rfh, '<:encoding(UTF-8)', 'data/planning_hebdo.csv') or die $!;
my $header = <$rfh>;
chomp $header;
my @cols = split /,/, $header;
shift @cols;

my %totals;
while (<$rfh>) {
    chomp;
    my @v = split /,/;
    shift @v;
    for my $i (0..$#cols) {
        my $act = $v[$i];
        $totals{$cols[$i]}{$act}++ if $act ne "Libre";
    }
}
close($rfh);

for my $jour (@cols) {
    print "\n$jour:\n";
    for my $act (sort keys %{$totals{$jour}}) {
        my $h = $totals{$jour}{$act} * 15 / 60;
        print sprintf("  %-12s : %.2f h\n", $act, $h);
    }
}
