# Copyright 2016 NeuroData (http://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# qa_func.py
# Created by Eric W Bridgeford on 2016-06-08.
# Email: ebridge2@jhu.edu

import nibabel as nb
import sys
import re
import os.path
import matplotlib
import numpy as np
from ndmg.utils import utils as mgu
from ndmg.stats.func_qa_utils import plot_timeseries, plot_signals, \
    registration_score
from ndmg.stats.qa_reg import reg_mri_pngs, plot_brain, plot_overlays
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly as py
import plotly.offline as offline
import pickle


class qa_func(object):
    def __init__(self):
        pass

    @staticmethod
    def load(filename):
        """
        A function for loading a qa_func object, so that we
        can perform group level quality control easily.

        **Positional Arguments:**

            filename: the name of the pickle file containing
                our qa_func object
        """
        with open(filename, 'rb') as f:
            obj = pickle.load(f)
        f.close()
        return obj

    def save(self, filename):
        """
        A function for saving a qa_func object.

        **Positional Arguments:**

            filename: the name of the file we want to save to.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        f.close()
        pass

    def func_preproc_qa(self, prep, qcdir):
        """
        A function for performing quality control given motion
        correction information. Produces plots of the motion correction
        parameters used.

        **Positional Arguments**

            prep:
                - the module used for preprocessing.
            scan_id:
                - the id of the subject.
            qcdir:
                - the quality control directory.
        """
        print "Performing QA for Functional Preprocessing..."
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
        func_name = mgu.get_filename(prep.motion_func)

        raw_im = nb.load(prep.func)
        raw_dat = raw_im.get_data()

        # plot the uncorrected brain. this brain, if motion
        # is significant, will show a poorly defined border
        # since the brain will be moving in time
        rawfig = plot_brain(raw_dat.mean(axis=3), minthr=10)

        mc_im = nb.load(prep.motion_func)
        mc_dat = mc_im.get_data()

        # plot the preprocessed brain. this brain should
        # look less blurred since the brain will be fixed in time
        # due to motion correction
        mcfig = plot_brain(prep_dat.mean(axis=3), minthr=10)
        nvols = mc_dat.shape[3]

        # get the functional preprocessing motion parameters
        mc_params = np.genfromtxt(prep.mc_params)

        # Note that our translational parameters (first 3 columns of motion
        # params) are already in mm. For the rotational params, we use
        # Power et. al and assume brain rad of 50 mm, and given our radial
        # coords translate back to euclidian space so our displacement of
        # the x, y, z rotations is the displacement of the outer edge
        # of the brain
        mc_params[:, 0:3] = 50*np.pi*mc_params[:, 0:3]/180

        fd_pars = np.zeros(mc_params.shape)

        # our array of the displacements in x, y, z translations and rotations
        # volume wise displacement parameters for each x, y, z trans/rotation
        vd_pars[1:None, :] = np.diff(mc_params[1:None, :], mc_params[0:-1, :])

        # using the displacements, compute the euclidian distance of the
        # movement from volume to volume, given no displacement at the start
        fd_pars = np.linalg.norm(vd_pars, axis=1)
        # separate out the translational and rotational parameters, so we can
        # use them for statistics later
        trans_pars = np.split(mc_params[:, 3:6], 3, axis=1)
        rot_pars = np.split(mc_params[:, 0:3], 3, axis=1)
        # list of lists, where each list is the parameter
        # we will want a plot of
        # note that fd_pars is just an array, so we need to make
        # it a single-element list
        mc_pars = [trans_pars, rot_pars, [fd_pars]]

        # names to append to plots so they can be found easily
        mp_names = ["FD", "trans", "rot"]
        # titles for the plots
        mp_titles = ["Framewise Displacement", "Translational Parameters",
                     "Rotational Parameters"]
        # list of lists of the line labels
        linelegs = [['x rot', 'y rot', 'z rot'],
                    ['x trans', 'y trans', 'z trans'], ['framewise']]
        xlab = 'Timepoint'
        ylab = 'Displacement'
        # iterate over tuples of the lists we store our plot variables in
        for (param_type, name, title, legs) in zip(mc_pars, mc_names,
                                                   glm_titles, linelegs):
            params = []
            labels = []
            # iterate over the parameters while iterating over the legend
            # labels for each param
            params = [param for param in param_types]
            labels = [' {} displacement'.format(leg) for leg in legs]
            fig = plot_signals(regs, labels, title=title,
                               xlabel=xlab, ylabel=ylab)

            fname_reg = "{}/{}_{}_parameters.png".format(qcdir,
                                                         func_name,
                                                         name)
            fig.savefig(fname_reg, format='png')
            plt.close(fig)
        self.fd_params
        mc_file = "{}/{}_stats.txt".format(qcdir, func_name)

        # framewise-displacement statistics
        prep.max_fd = np.max(fd_pars)
        prep.mean_fd = np.mean(fd_pars)
        prep.std_fd = np.std(fd_pars)
        # number of framewise displacements greater than .2 mm
        prep.num_fd_gt_200um = np.sum(fd_pars > .2)
        # number of framewise displacements greater than .5 mm
        prep.num_fd_gt_500um = np.sum(fd_pars > .5)
        fstat.close()
        pass

    def anat_preproc_qa(self, prep, qa_dir):
        """
        A function that produces anatomical preprocessing quality assurance
        figures.

        **Positional Arguments:**

            - prep:
                - the preprocessing object.
            - qa_dir:
                - the directory to place figures.
        """
        print "Performing QA for Anatoical Preprocessing..."
        figs = {}
        # produce plots for the raw anatomical image
        figs['raw_anat'] = plot_brain(prep.anat)
        # produce the preprocessed anatomical image plot
        figs['preproc'] = plot_brain(prep.anat_preproc)
        # produce the preprocessed skullstripped anatomical image plot
        figs['preproc_brain'] = plot_overlays(prep.anat_preproc,
                                              prep.anat_preproc_brain)
        # save iterator
        for plotname, fig in figs.iteritems():
            fname = "{}/{}_{}.png".format(qa_dir, prep.anat_name, plotname)
            fig.tight_layout()
            fig.savefig(fname)
            plt.close(fig)
        pass

    def self_reg_qa(self, freg, qa_dirs):
        """
        A function that produces self-registration quality control figures.

        **Positional Arguments:**

            freg:
                - the func_register object from registration.
            sreg_func_dir:
                - the directory to place functional qc images.
        """
        print "Performing QA for Self-Registration..."
        # overlap statistic for the functional and anatomical
        # skull-off brains
        (sreg_sc, sreg_fig) = registration_score(
            freg.sreg_brain,
            freg.t1w_brain
        )
        self.self_reg_sc = sreg_sc
        # use the jaccard score in the filepath to easily
        # identify failed subjects
        sreg_f_final = "{}/{}_jaccard_{:.0f}".format(
            qa_dirs['sreg_f'],
            freg.sreg_strat,
            self.self_reg_sc*1000
        )
        sreg_a_final = "{}/{}_jaccard_{:.0f}".format(
            qa_dirs['sreg_a'],
            freg.sreg_strat,
            self.self_reg_sc*1000
        )
        cmd = "mkdir -p {} {}".format(sreg_f_final, sreg_a_final)
        mgu.execute_cmd(cmd)
        func_name = mgu.get_filename(freg.sreg_brain)
        t1w_name = mgu.get_filename(freg.t1w)
        sreg_fig.savefig(
            "{}/{}_epi2t1w.png".format(sreg_f_final, func_name)
        )
        # produce plot of the white-matter mask used during bbr
        if freg.wm_mask is not None:
            mask_dat = nb.load(mask).get_data()
            t1w_dat = nb.load(freg.t1w_brain).get_data()
            f_mask = plot_overlays(t1w_dat, mask_dat, minthr=0, maxthr=100)
            fname_mask = "{}/{}_{}.png".format(sreg_a_final, anat_name,
                                               "_wm_mask")
            f_mask.savefig(fname_mask, format='png')
            plt.close(f_mask)

        plt.close(sreg_fig)
        pass

    def temp_reg_qa(self, freg, qa_dirs):
        """
        A function that produces self-registration quality control figures.

        **Positional Arguments:**

            freg:
                - the functional registration object.
            qa_dirs:
                - a dictionary of the directories to place qa files.
        """
        print "Performing QA for Template-Registration..."
        # overlap statistic and plot btwn template-aligned fmri
        # and the atlas brain that we are aligning to
        (treg_sc, treg_fig) = registration_score(
            freg.taligned_epi,
            freg.atlas_brain,
            edge=True
        )
        # use the registration score in the filepath for easy
        # identification of failed subjects
        self.temp_reg_sc = treg_sc
        treg_f_final = "{}/{}_jaccard_{:.0f}".format(
            qa_dirs['treg_f'],
            freg.treg_strat,
            self.temp_reg_sc*1000
        )
        treg_a_final = "{}/{}_jaccard_{:.0f}".format(
            qa_dirs['treg_a'],
            freg.treg_strat,
            self.temp_reg_sc*1000
        )
        cmd = "mkdir -p {} {}".format(treg_f_final, treg_a_final)
        mgu.execute_cmd(cmd)
        func_name = mgu.get_filename(freg.taligned_epi)
        treg_fig.savefig(
            "{}/{}_epi2temp.png".format(treg_f_final, func_name)
        )
        plt.close(treg_fig)
        t1w_name = mgu.get_filename(freg.taligned_t1w)
        # overlap between the template-aligned t1w and the atlas brain
        # that we are aligning to
        t1w2temp_fig = plot_overlays(freg.taligned_t1w, freg.atlas_brain,
                                     edge=True, minthr=0, maxthr=100)
        t1w2temp_fig.savefig(
            "{}/{}_t1w2temp.png".format(treg_a_final, t1w_name)
        )
        plt.close(t1w2temp_fig)
        # produce cnr, snr, and mean plots for temporal voxelwise statistics
        self.voxel_qa(freg.epi_aligned_skull, freg.atlas_mask, treg_f_final)
        pass

    def voxel_qa(self, func, mask, qadir):
        """
        A function to compute voxelwise statistics, such as voxelwise mean,
        voxelwise snr, voxelwise cnr, for an image, and produce related
        qa plots.

        **Positional Arguments:**

            func:
                - the path to the functional image we want statistics for.
            mask:
                - the path to the anatomical mask.
            qadir:
                - the directory to place qa images.
        """
        # estimating mean signal intensity and deviation in brain/non-brain
        fmri = nb.load(func)
        mask = nb.load(mask)
        fmri_dat = fmri.get_data()
        mask_dat = mask.get_data()

        # threshold to identify the brain and non-brain regions of the atlas
        brain = fmri_dat[mask_dat > 0, :]
        non_brain = fmri_dat[mask_dat == 0, :]
        # identify key statistics
        mean_brain = brain.mean()  # mean of each brain voxel (signal)
        std_nonbrain = np.nanstd(non_brain)  # std of nonbrain voxels (noise)
        std_brain = np.nanstd(brain)  # std of brain voxels (contrast)
        self.snr = mean_brain/std_nonbrain  # definition of snr
        self.cnr = std_brain/std_nonbrain  # definition of cnr

        func_name = mgu.get_filename(func)

        np.seterr(divide='ignore', invalid='ignore')
        mean_ts = fmri_dat.mean(axis=3)  # temporal mean
        snr_ts = np.divide(mean_ts, std_nonbrain)  # temporal snr
        # temporal cnr
        cnr_ts = np.divide(np.nanstd(fmri_dat, axis=3), std_nonbrain)

        plots = {}
        plots["mean"] = plot_brain(mean_ts, minthr=10)
        plots["snr"] = plot_brain(snr_ts, minthr=10)
        plots["cnr"] = plot_brain(cnr_ts, minthr=10)
        for plotname, plot in plots.iteritems():
            fname = "{}/{}_{}.png".format(qadir, func_name, plotname)
            plot.savefig(fname, format='png')
            plt.close(plot)
        pass

    def nuisance_qa(self, nuisobj, qcdir):
        """
        A function to assess the quality of nuisance correction.

        **Positional Arguments**

            nuisobj:
                - the nuisance correction object.
            qcdir:
                - the directory to place quality control images.
        """
        print "Performing QA for Nuisance..."
        maskdir = "{}/{}".format(qcdir, "masks")
        glmdir = "{}/{}".format(qcdir, "glm_correction")
        fftdir = "{}/{}".format(qcdir, "filtering")

        cmd = "mkdir -p {} {} {}".format(qcdir, maskdir, glmdir)
        mgu.execute_cmd(cmd)

        anat_name = mgu.get_filename(nuisobj.smri)
        t1w_dat = nb.load(nuisobj.smri).get_data()
        # list of all possible masks
        masks = [nuisobj.lv_mask, nuisobj.wm_mask, nuisobj.gm_mask,
                 nuisobj.er_wm_mask]
        masknames = ["csf_mask", "wm_mask", "gm_mask", "eroded_wm_mask"]
        # iterate over masks for existence and plot overlay if they exist
        # since that means they were used at some point
        for mask, maskname in zip(masks, masknames):
            if mask is not None:
                mask_dat = nb.load(mask).get_data()
                # produce overlay figure between the t1w image that has
                # segmentation performed on it and the respective mask
                f_mask = plot_overlays(t1w_dat, mask_dat, minthr=0, maxthr=100)
                fname_mask = "{}/{}_{}.png".format(maskdir, anat_name,
                                                   maskname)
                f_mask.savefig(fname_mask, format='png')
                plt.close(f_mask)

        # GLM regressors we could have
        glm_regs = [nuisobj.csf_reg, nuisobj.wm_reg, nuisobj.friston_reg]
        glm_names = ["csf", "wm", "friston"]
        glm_titles = ["CSF Regressors", "White-Matter Regressors",
                      "Friston Motion Regressors"]
        # whether we should include legend labels
        label_include = [True, True, False]
        # iterate over tuples of our plotting variables
        for (reg, name, title, lab) in zip(glm_regs, glm_names, glm_titles,
                                           label_include):
            # if we have a particular regressor
            if reg is not None:
                regs = []
                labels = []
                nreg = reg.shape[1]  # number of regressors for a particular
                                     # nuisance variable
                # store each regressor as a element of our list
                regs = [reg[:, i] for i in range(0, nreg)]
                # store labels in case they are plotted
                labels = ['{} reg {}'.format(name, i) for i in range(0, nreg)]
                # plot each regressor as a line
                fig = plot_signals(regs, labels, title=title,
                                   xlabel='Timepoint', ylabel='Intensity',
                                   lab_incl=lab)
                fname_reg = "{}/{}_{}_regressors.png".format(glmdir,
                                                             anat_name,
                                                             name)
                fig.savefig(fname_reg, format='png')
                plt.close(fig)
        # signal before compared with the signal removed and
        # signal after correction
        fig_glm_sig = plot_signals(
            [nuisobj.cent_nuis, nuisobj.glm_sig, nuisobj.glm_nuis],
            ['Before', 'Regressed Sig', 'After'],
            title='Impact of GLM Regression on Average GM Signal',
            xlabel='Timepoint',
            ylabel='Intensity'
        )
        fname_glm_sig = '{}/{}_glm_signal_cmp.png'.format(glmdir, anat_name)
        fig_glm_sig.savefig(fname_glm_sig, format='png')
        plt.close(fig_glm_sig)

        # Frequency Filtering
        if nuisobj.fft_reg is not None:
            cmd = "mkdir -p {}".format(fftdir)
            mgu.execute_cmd(cmd)
            # start by just plotting the average fft of gm voxels and
            # compare with average fft after frequency filtering
            fig_fft_pow = plot_signals(
                [nuisobj.fft_bef, nuisobj.fft_reg],
                ['Before', 'After'],
                title='Average Gray Matter Power Spectrum',
                xlabel='Frequency',
                ylabel='Power',
                xax=nuisobj.freq_ra)
            fname_fft_pow = '{}/{}_fft_power.png'.format(fftdir, anat_name)
            fig_fft_pow.savefig(fname_fft_pow, format='png')
            plt.close(fig_fft_pow)
            # plot the signal vs the regressed signal vs signal after
            fig_fft_sig = plot_signals(
                [nuisobj.glm_nuis, nuisobj.fft_sig, nuisobj.fft_nuis],
                ['Before', 'Regressed Sig', 'After'],
                title='Impact of Frequency Filtering on Average GM Signal',
                xlabel='Timepoint',
                ylabel='Intensity')
            fname_fft_sig = '{}/{}_fft_signal_cmp.png'.format(
                fftdir,
                anat_nam
            )
            fig_fft_sig.savefig(fname_fft_sig, format='png')
            plt.close(fig_fft_sig)
        pass

    def roi_ts_qa(self, timeseries, func, anat, label, qcdir):
        """
        A function to perform ROI timeseries quality control.

        **Positional Arguments**

            timeseries:
                - a path to the ROI timeseries.
            func:
                - the functional image that has timeseries
                extract from it.
            anat:
                - the anatomical image that is aligned.
            label:
                - the label in which voxel timeseries will be
                downsampled.
            qcdir:
                - the quality control directory to place outputs.
        """
        print "Performing QA for ROI Timeseries..."
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)

        # overlap between the temp-aligned t1w and the labelled parcellation
        reg_mri_pngs(anat, label, qcdir, minthr=10, maxthr=95)
        # overlap between the temp-aligned fmri and the labelled parcellation
        reg_mri_pngs(func, label, qcdir, minthr=10, maxthr=95)
        # plot the timeseries for each ROI and the connectivity matrix
        plot_timeseries(timeseries, qcdir=qcdir)
        pass

    def voxel_ts_qa(self, timeseries, voxel_func, atlas_mask, qcdir):
        """
        A function to analyze the voxel timeseries extracted.

        **Positional Arguments**

            voxel_func:
                - the functional timeseries that
              has voxel timeseries extracted from it.
            atlas_mask:
                - the mask under which
              voxel timeseries was extracted.
            qcdir:
                - the directory to place qc in.
        """
        print "Performing QA for Voxel Timeseries..."
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
        # plot the voxelwise signal with respect to the atlas to
        # get an idea of how well the fmri is masked
        reg_mri_pngs(voxel_func, atlas_mask, qcdir,
                     loc=0, minthr=10, maxthr=95)
        pass
