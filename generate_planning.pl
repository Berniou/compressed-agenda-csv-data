#!/usr/bin/perl
use strict;
use warnings;

my @jours = qw(dimanche lundi mardi mercredi jeudi vendredi samedi);

# Créer dossier data si besoin
mkdir "data" unless -d "data";

open(my $fh, '>:encoding(UTF-8)', 'data/planning_hebdo.csv') or die "Impossible d'ouvrir le fichier: $!";
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

            if ($jour eq "dimanche") {
                if (($minute >= 0 && $minute < 540) || ($minute >= 1260 && $minute < 1440)) {
                    $act = "Sommeil";
                } elsif ($minute >= 540 && $minute < 600) {
                    $act = "Libre";
                } elsif ($minute >= 600 && $minute < 840) {
                    $act = "Eglise";
                } elsif ($minute >= 840 && $minute < 1020) {
                    $act = "Famille";
                } elsif ($minute >= 1020 && $minute < 1110) {
                    $act = "Cuisine";
                } elsif ($minute >= 1110 && $minute < 1200) {
                    $act = "Ménage";
                } elsif ($minute >= 1200 && $minute < 1260) {
                    $act = "Lessive";
                }
            }
            elsif ($jour =~ /^(lundi|mercredi|vendredi)$/) {
                if (($minute >= 0 && $minute < 420) || ($minute >= 1380 && $minute < 1440)) {
                    $act = "Sommeil";
                } elsif ($minute >= 420 && $minute < 480) {
                    $act = "Prière";
                } elsif ($minute >= 480 && $minute < 540) {
                    $act = "Libre";
                } elsif ($minute >= 540 && $minute < 1215) {
                    $act = "Travail";
                } elsif ($minute >= 1215 && $minute < 1275) {
                    $act = "Candidature";
                } elsif ($minute >= 1275 && $minute < 1365) {
                    $act = "Cuisine";
                } elsif ($minute >= 1365 && $minute < 1380) {
                    $act = "Libre";
                }
            }
            elsif ($jour =~ /^(mardi|jeudi)$/) {
                if (($minute >= 0 && $minute < 420) || ($minute >= 1380 && $minute < 1440)) {
                    $act = "Sommeil";
                } elsif ($minute >= 420 && $minute < 480) {
                    $act = "Prière";
                } elsif ($minute >= 480 && $minute < 540) {
                    $act = "Libre";
                } elsif ($minute >= 540 && $minute < 1215) {
                    $act = "Travail";
                } elsif ($minute >= 1215 && $minute < 1275) {
                    $act = "Candidature";
                } elsif ($minute >= 1275 && $minute < 1365) {
                    $act = "Ménage";
                } elsif ($minute >= 1365 && $minute < 1380) {
                    $act = "Libre";
                }
            }
            elsif ($jour eq "samedi") {
                if (($minute >= 0 && $minute < 420) || ($minute >= 480 && $minute < 540)) {
                    $act = "Sommeil";        # 00h-07h + 08h-09h = 8h
                } elsif ($minute >= 420 && $minute < 480) {
                    $act = "Prière";         # 07h-08h = 1h
                } elsif ($minute >= 540 && $minute < 660) {
                    $act = "FI";             # 09h-11h = 2h
                } elsif ($minute >= 660 && $minute < 1260) {
                    $act = "Libre";
                } elsif ($minute >= 1260 && $minute < 1350) {
                    $act = "Ménage";         # 21h-22h30 = 1h30
                } elsif ($minute >= 1350 && $minute < 1440) {
                    $act = "Libre";
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

print "=== Aperçu des 20 premières lignes ===\n";
print @preview;
print "\nFichier généré : data/planning_hebdo.csv\n";

# Vérification rapide des volumes par jour
print "\n=== Volumes générés (créneaux de 15 min) ===\n";
open(my $rfh, '<:encoding(UTF-8)', 'data/planning_hebdo.csv') or die $!;
my $header = <$rfh>;
chomp $header;
my @cols = split /,/, $header;
shift @cols; # enlever heure

my %totals;
for my $c (@cols) { $totals{$c} = {}; }

while (<$rfh>) {
    chomp;
    my @v = split /,/;
    my $h = shift @v;
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
