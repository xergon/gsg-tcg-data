           Brief explanation of the contents of the 2nd Deep Data Releases

           Deep Data Release 2 consists of the full-depth data of the following 9 MHONGOOSE
           galaxies: J0135-41, J0335-24, J0429-27, J0459-26, J0546-52, J1103-23, J2009-61,
           J2257-41, J2357-32.

           Note that J2357-23 contains Magellanic Stream HI overlapping with the galaxy. This
           release therefore includes moment maps with the Stream HI either included
           (J2357-32_orig) or removed (J2357-32).


               When using these data please include a reference to the MHONGOOSE survey paper:
               de Blok et al (2024), A&A, 688, A109; https://ui.adsabs.harvard.edu/abs/
               2024A%26A...688A.109D/abstract


           Please see the webpage at https://mhongoose.astron.nl/sample.html and the
           MHONGOOSE survey paper for further details on the global properties of these galaxies.

           The release contains three main directories, containing the data cubes, the moment maps
           (including primary beam maps and masks), and data release documents (including Atlas
           pages and Legacy Survey overlays). It is recommended to rst have a look at the PDF
             les in the documents folder to familiarise yourself with the galaxies prior to downloading
           large numbers of data sets. A brief description of the contents of each directory is given
           below.

           Cubes

           We provide data cubes for the target galaxies at six standard resolutions. The cubes have
           a velocity resolution of 1.4 km/s and a velocity range of ~1000 km/s straddling the
           velocity of the target galaxy. The actual range may vary slightly depending on whether the
           cube contains any agged Milky Way channels. The cubes measure 1.5 x 1.5 degrees in
           angular size. This is larger than the MeerKAT primary beam of ~1 degree due to the
           signi cant number of sources that can be detected in the outer eld for some of the
           galaxies.

           In addition to the full data reduction as described in the survey paper, we added an extra
           step, consisting of a nal residual continuum subtraction in the image plane using the
           imcontsub routine developed by Sphesihle Makhathini (https://github.com/
           laduma-dev/contsub). This is done after the creation of the moment maps as
           described in the survey paper. In this step, we rst use imcontsub to mask the data
           cubes using the 3D moment map masks created by SoFiA-2 (thus removing all detected
           emission). A low-order polynomial is then tted to all spectra in the masked cubes. These
             tted cubes are subtracted from the respective image cubes, after which new moment
           maps are created using SoFiA-2 (using the same parameter le). The di erence between
           initial and nal moment maps is negligible, but the procedure does improve the statistics
           of the noise, and automatically removes residual continuum features that are not visible in
           individual channels but were detected by SoFiA-2 in the initial moment-map run.




                                                                        fi
          fi          fl   fi              fi      fi         fi   fi
     fi
fi
fi                                                                           ff
     We include cubes at various resolutions, covering the HI resolution range available to
     MeerKAT, created using a combination of robust weightings and taperings. See the
     MHONGOOSE survey paper and speci cally Table 4 therein, which is reproduced below.
     The actual beam sizes can be found in the headers, and the noise can be directly
     measured in the relevant channels. Small variations with respect to the indicative values
     should be expected, depending on declination, e ective observing time, amount of data
      agged etc. Due to their large size the r00_t00 cubes are not included, but they are
     available upon request. All relevant features in the r00_t00 cubes are also visible in the
     r05_t00 cubes at slightly reduced resolution.

     File names contain the galaxy HIPASS identi cation (J*), the robust value (r??) and the
     taper value (t??). These are also listed in the Table below.


                                                            de Blok, W. J. G., et al.: A&A, 688, A109 (2024)

        Table 4. Standard resolutions.

                                                                                                                                                1
                                                                                                                    1 ,1ch         3 ,16 km s
               Label         Robust      Taper     Pixel      bmaj         bmin         bPA      Noise        log NHI        log NHI                log MHI
                              value       (00 )     (00 )     (00 )        (00 )        ()    (mJy beam 1 )     (cm 2 )          (cm 2 )              (M )
               (1)             (2)        (3)       (4)       (5)          (6)          (7)        (8)            (9)             (10)                (11)
               r10_t90          1.0        90       30        94.2         91.2          47   0.318 ± 0.011     16.76             17.77              6.05
               r05_t60          0.5        60       20        65.3         64.0          92   0.250 ± 0.009     16.97             17.98              5.95
               r15_t00          1.5         0        7        34.4         25.4         135   0.154 ± 0.004     17.44             18.44              5.74
               r10_t00          1.0         0        5        26.4         18.2         136   0.150 ± 0.004     17.69             18.69              5.73
               r05_t00          0.5         0        3        14.1          9.7         137   0.171 ± 0.005     18.29             19.29              5.78
               r00_t00          0.0         0        2         8.2          7.1         142   0.219 ± 0.007     18.77             19.77              5.89
        Notes. (1) Label used to refer to this resolution. (2) Robustness weighting value. (3) Taper used. “0” mean no taper. (4) Pixel size of the data cubes
        and moment maps. (5) Average major axis beam size. (6) Average minor axis beam size. (7) Average position angle of major axis of beam. (8)
        Noise per channel. (9) 1 , one-channel column density sensitivity. (10) 3 , 16 km s 1 column density sensitivity. (11) H i mass sensitivity for a
        3 , 50 km s 1 unresolved source at 10 Mpc.



     Moment          Maps
      with the initial pipeline flags, these flags are then extended such
      that if more than   half of the visibilities at a certain observing
        time are flagged, all data at that time are flagged. Similarly for
     Wethe  frequency channels: if more than half of the data in a fre-
            provide      zeroth, rst and second moment maps at all standard resolutions for the
        quency channel are flagged, then all data at that frequency are
     target     galaxies.
        flagged. These          These
                        final flagging     were
                                       steps        produced
                                              complete the           using
                                                            reduction of a SoFiA-2 based on the imcontsub cubes
        single-track observation and the individual measurement sets are
     (see    ready Cubes
        now the                 section
                    to be combined   and for above).       The
                                              the full-depth      mosto important details are that we used the S+C
                                                             data cubes
       nder
        be      with spatial kernels of 0, 4 pixels, spectral kernels of 0, 9, 25 channels, and a
           created.
     threshold of 4 times the local rms. In terms of reliability we used a minSNR value of 5.0
        5.6. Standard resolutions
     and a reliability threshold of 0.8. The latter value was usually not relevant, as in the very
        MeerKAT is capable of producing high-quality images over a
     large      majority
        large range           ofresolution
                     in angular    cases(Fig.the       detected
                                                 1), resulting           objects were very clearly separated from the
                                                                in mapping
     reliability
        of compact,noise      distribution,
                      high-column                soasthat
                                    density sources,    well asthe     value of minSNR was the only relevant parameter.
                                                                  extended,
        low-column density features (Fig. 2). It is difficult to capture
     In this
         termswealthof
                     of kernels
                        structure in we   found
                                     a single        thatat using
                                              data cube                 larger spatial kernels than used here led to over-
                                                             a single reso-
     smoothing
        lution. For and
                    MHONGOOSE,the weaddition
                                          have of      noise
                                               therefore defined insixthe   moment maps (i.e., MeerKAT is very e cient at
                                                                        stan-
        dard resolutions for our data products, which cover the angular
     picking       up HI emission and large smoothing factors give diminishing returns). More
        resolution range of MeerKAT as indicated in Fig. 2.
     information        can also
             These di↵erent            beare
                              resolutions  found
                                              achievedin by
                                                         thechanging
                                                                 Survey   the Paper.
       robust weighting parameter used in creating the data cubes, and,
       for the two lowest resolutions, some additional tapering. We
     Moment
       find        maps
            that these          are combinations
                        six standard   organisedgiveasa follows:
                                                           comprehensive for each galaxy there are six subdirectories
       overview   of the  H   morphology    and  kinematics of the sample  Fig. 5. Sensitivities of the full-depth data cubes. The top panel shows the
     corresponding to each of the standard
                            i                                         resolutions.
                                                                           average noiseIn     each
                                                                                          per 1.4  km s 1 of    these
                                                                                                           channel          arestandard
                                                                                                                    for the six    the resolutions,
                                                                                                                                           respective  as
       galaxies.
     moment        maps        (*mom0*,          *mom1*,          *mom2*),       a
                                                                           averaged map
                                                                                     over      showing
                                                                                           full-depth            the
                                                                                                       observations  of number          of
                                                                                                                         ten galaxies (cf.
           Table 4 and Fig. 5 show the average noise per channel and bars show the rms di↵erence in noise levels between the ten galax-      channels
                                                                                                                                           Fig. 1). Error
       beam size as derived
     contributing         to afromoment-map
                                      the full-depth standard cubes
                                                          pixel     of ten ies, butaaretwo
                                                                  (*chan*),                    dimensional
                                                                                        generally                      maskthan the
                                                                                                     comparable to or smaller      identifying
                                                                                                                                           symbol size.the
       galaxies available at the time of writing. We also list the col- The bottom panel shows the 3 , 16 km s 1 column density sensitivities.
       umn density sensitivities where we give the values for 1 over a These are the same points as shown in Fig. 2.
       single channel, as well as the 3 over 16 km s 1 values used in
       Fig. 2. Finally, we also list the 3 H i mass detection limit for an
       unresolved source, assuming a distance of 10 Mpc (the median
       distance of the galaxies in the sample) and a velocity width of ficiently short baselines (cf. Table 3). This can be seen by the
                      fi
fi
fl                                                    fi              fi           ff                                                ffi
detected sources (*mask-2d*) and a (compressed) 3D mask that was used to create the
moment maps (*mask.fits.gz; except for r00_t00). In addition a zeroth-moment map
which has been primary-beam corrected is also provided (*mom0_pb*) as well as the
primary beam map used (*primbeam*). We only provide a primary-beam image and not
a primary-beam cube as any change in the size of primary beam is negligible over the
velocity ranges presented here.
          Atlas Pages

          We provide Atlas pages in PDF format for a quick visual overview of the HI distribution in
          these galaxies. These can be found in the documents/Atlas directory

          Top row, rst panel: Optical colour image created from the Dark Energy Camera Legacy
          Survey (DECaLS) DR10 release.

          Top row, second panel: Zeroth-moment (integrated intensity) map of the target galaxy
          based on r00_t00 data (high resolution). The lowest contour level corresponds to the S/
          N=3 level (see below). Contours then increase by a factor 2n where n=0,2,4,… . Values are
          given in the legend in the panel. The grey scale runs from 0 to 99.99 percentile with a
          sqrt stretch. The map displayed here is primary-beam corrected.

          Top row, third panel: Zeroth-moment map of the target galaxy based on r10_t00 data
          (medium resolution). The lowest contour level corresponds to the S/N=3 level (see below).
          Contours are then spaced as 2n where n=0,2,4,… . Values are given in the legend in the
          panel. The grey scale runs from 0 to 99.99 percentile with a sqrt stretch. The map
          displayed here is primary-beam corrected.

          Top row, fourth panel: First-moment (intensity-weighted velocity) map of the target
          galaxy based on r10_t00 data. The thick black contour indicates an indicative systemic
          velocity as determined by the parametrisation by SoFiA-2. Contours are then spaced by
          5, 10, or 20 km/s as indicated in the panel. Blue colours indicate the approaching side,
          red colours the receding side. The indicative systemic velocity used here does not
          necessarily represent the actual systemic velocity of the target galaxy.

          Bottom-left panel: multi-resolution HI map of the target galaxy. This shows the S/N=3
          contours (see below) for a range of resolutions, derived from di erent weighting and
          tapering combinations. The column density that belongs to each of the contours is
          indicated in the colour bar at the corresponding colour. The geometric mean size of the
          beam size is also given there. The background image is the r-band DR10 legacy survey
          image.

          Centre-right panel: position-velocity slice along an indicative major axis position angle.
          The value of the PA is indicated in the panel. This value does not necessarily equal the
          proper kinematical PA as would be derived from a full kinematical analysis. The grayscale
          contours have values 3*rms*2n, where n=0,1,2,…. The blue contour indicates 3*rms, the
          red contour -2.5*rms. The horizontal green line show the indicative systemic velocity. The
          grayscale runs from -1.5*rms to the 99.95 percentile with an asinh stretch.

          Bottom-right panel: Low-resolution integrated HI map (based on r05_t60)
          encompassing all sources detected in the eld. The lowest (blue) contour is the S/N=3
          contour. Levels then increase by factors 2n, where n=0,2,4,… .

          The S/N=3 contour
          In the zeroth moment panels, the S/N=3 contour level is speci ed in the text at the
          bottom of the panel. The S/N=3 contour is calculated by using an S/N map which is
          de ned as the ratio of the zeroth-moment map and a noise map. The latter is calculated
          as [rms * dv * sqrt(nchan)], where dv is the channel width of the cube, nchan is




                                                                   ff
                                                              fi
                                          fi
     fi
fi
the number of channels in that particular line of sight that contribute to the zeroth
moment map and rms is the noise in a single channel. The column density associated
with S/N=3 is then calculated by taking the median column density of the pixels which
have S/N values in the S/N map between 2.75 < S/N < 3.25.

Multi-resolution overlays
For each galaxy the documents/MultiRes directory contains multi-resolution HI
overlays on optical grz Legacy Survey images. The contour levels for each resolution are
listed in the bottom-left of the gure and are again multiples of the S/N=3 contour as
described above for the Atlas pages. Yellow: r10_t90; purple: r05_t60; blue: r15_t00;
green: r10_t00; red: r05_t00.

The HI colour image overlay in yellow-orange is created by combining the zeroth-moment
maps of the above standard resolutions using an algorithm that mimics the “screen” layer
overlay option in Gimp image editing software. The HI overlay image was created to
simultaneously show the low- and high-column density features and the image values
should not be used for quantitive purposes.

For each galaxy a number of di erent versions of its multi-resolution image are included:

*_multihi_decals_r05 = this shows an overlay of the combined HI column density
image on the grz optical image. The lower column densities are represented by contours
from each of the standard resolutions as described above.

*_multihi_decals_r05 = as the previous image, except the r05_t00 contour is not
plotted to more clearly show the HI image.

*_multihi_decals_nocontours = only the HI image overlay is shown and no
contours.

*_nomultihi_decals_nor05 = neither HI image, nor the r05_t00 contours are
plotted to better show the optical galaxy.




                        ff
                   fi
