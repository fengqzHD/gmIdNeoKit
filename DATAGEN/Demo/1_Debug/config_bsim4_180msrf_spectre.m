% Configuration for techsweep_spectre_run.m
% Boris Murmann, Stanford University
% Tested with MMSIM12.11.134
% September 12, 2017
% Changed by Fengqi Zhang, Columbia University, July 2019
% Reset the Fils to the Skeleton
% Usage :
% 1. Replace XXX_ with Desired Name & Setting
% 2. Set the Sweep parameters section
% 3. Check the BSIM model for finger setting of nf or m and change _finger_
% 4. Debug the techsweep file with spectre_debug
% Log of Usage
% Fengqi Zhang, Columbia University, May 2020
% Initial -> Debug
% 1. XXX_tech -> 180msrf
% 2. XXX_corner -> tt
% 3. XXX_modelPath-> /tech/tsmc/tsmc180/tsmc180_rhuq_MEA/tsmc180/models/spectre/cmn018_assp_v1d3
% 4. XXX_model    -> BSIM4 V4.5
% 5. XXX_nmosType -> nch
% 6. XXX_pmosType -> pch
% 7. XXX_temp     -> 27
% 8. Setting of Sweep Parameters
% 9. Add m=1 related to mn & mp and change _finger_ to nf
function c = config_bsim4_180msrf_spectre

% Models and file paths
c.modelfile = '"/tech/tsmc/tsmc180/tsmc180_rhuq_MEA/tsmc180/models/spectre/cmn018_assp_v1d3.scs" section=tt';
c.modelinfo = '180msrf, BSIM4 V4.5';
c.corner = 'tt';
c.temp = 27 + 273;
c.modeln = 'nch';
c.modelp = 'pch';
c.savefilen = sprintf('180msrf-%s-%s', c.modeln, c.corner);
c.savefilep = sprintf('180msrf-%s-%s', c.modelp, c.corner);
c.simcmd = 'spectre -64 techsweep_180msrf.scs +log techsweep_180msrf.out';
c.outfile = 'techsweep_180msrf.raw';
c.sweep = 'sweepvds_sweepvgs-sweep';
c.sweep_noise = 'sweepvds_noise_sweepvgs_noise-sweep';

% Sweep parameters
c.VGS_step = 25e-3;
c.VDS_step = 25e-3;
c.VSB_step = 0.2;
c.VGS_max = 1.8;
c.VDS_max = 1.8;
c.VSB_max = 0.6;
c.VGS = 0:c.VGS_step:c.VGS_max;
c.VDS = 0:c.VDS_step:c.VDS_max;
c.VSB = flip(0:c.VSB_step:c.VSB_max);
%c.LENGTH = [0.13,0.15,0.18,0.2,0.25,0.3,0.35,0.5,0.6,0.7,0.8,1.0,1.5,2.0]; %c.LENGTH = [(0.03:0.01:0.06) (0.08:0.02:0.2) (0.25:0.05:1)];
c.LENGTH = [0.18,0.25,0.35];
c.WIDTH = 4;
c.NFING = 4;

% Variable mapping
c.outvars =                  {'ID','VT','IGD','IGS','GM','GMB','GDS','CGG','CGS','CSG','CGD','CDG','CGB','CDD','CSS','FUG', 'GMOVERID', 'ROUT', 'VDSAT'};
% NType-Device
c.n{1}= {'mn:ids','A',         [1    0    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{2}= {'mn:vth','V',         [0    1    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{3}= {'mn:igd','A',         [0    0    1     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{4}= {'mn:igs','A',         [0    0    0     1     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{5}= {'mn:gm','S',          [0    0    0     0     1    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{6}= {'mn:gmbs','S',        [0    0    0     0     0    1     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{7}= {'mn:gds','S',         [0    0    0     0     0    0     1     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{8}= {'mn:cgg','F',         [0    0    0     0     0    0     0     1     0     0     0     0     0     0     0     0        0            0          0  ]};
c.n{9}= {'mn:cgs','F',         [0    0    0     0     0    0     0     0    -1     0     0     0     0     0     0     0        0            0          0  ]};
c.n{10}={'mn:cgd','F',         [0    0    0     0     0    0     0     0     0     0    -1     0     0     0     0     0        0            0          0  ]};
c.n{11}={'mn:cgb','F',         [0    0    0     0     0    0     0     0     0     0     0     0    -1     0     0     0        0            0          0  ]};
c.n{12}={'mn:cdd','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     1     0     0        0            0          0  ]};
c.n{13}={'mn:cdg','F',         [0    0    0     0     0    0     0     0     0     0     0    -1     0     0     0     0        0            0          0  ]};
c.n{14}={'mn:css','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     0     1     0        0            0          0  ]};
c.n{15}={'mn:csg','F',         [0    0    0     0     0    0     0     0     0    -1     0     0     0     0     0     0        0            0          0  ]};
c.n{16}={'mn:cjd','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     1     0     0        0            0          0  ]};
c.n{17}={'mn:cjs','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     0     1     0        0            0          0  ]};
c.n{18}={'mn:fug','Hz',        [0    0    0     0     0    0     0     0     0     0     0     0     0     0     0     1        0            0          0  ]};
c.n{19}={'mn:gmoverid','V',    [0    0    0     0     0    0     0     0     0     0     0     0     0     0     0     0        1            0          0  ]};
c.n{20}={'mn:rout','Ohm',      [0    0    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            1          0  ]};
c.n{21}={'mn:vdsat','V',       [0    1    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0          1  ]};

% PType-Device
%                            {'ID','VT','IGD','IGS','GM','GMB','GDS','CGG','CGS','CSG','CGD','CDG','CGB','CDD','CSS','FUG', 'GMOVERID', 'ROUT', 'VDSAT'};
c.p{1}= {'mp:ids','A',         [-1   0    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{2}= {'mp:vth','V',         [0   -1    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{3}= {'mp:igd','A',         [0    0   -1     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{4}= {'mp:igs','A',         [0    0    0    -1     0    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{5}= {'mp:gm','S',          [0    0    0     0     1    0     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{6}= {'mp:gmbs','S',        [0    0    0     0     0    1     0     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{7}= {'mp:gds','S',         [0    0    0     0     0    0     1     0     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{8}= {'mp:cgg','F',         [0    0    0     0     0    0     0     1     0     0     0     0     0     0     0     0        0            0          0  ]};
c.p{9}= {'mp:cgs','F',         [0    0    0     0     0    0     0     0    -1     0     0     0     0     0     0     0        0            0          0  ]};
c.p{10}={'mp:cgd','F',         [0    0    0     0     0    0     0     0     0     0    -1     0     0     0     0     0        0            0          0  ]};
c.p{11}={'mp:cgb','F',         [0    0    0     0     0    0     0     0     0     0     0     0    -1     0     0     0        0            0          0  ]};
c.p{12}={'mp:cdd','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     1     0     0        0            0          0  ]};
c.p{13}={'mp:cdg','F',         [0    0    0     0     0    0     0     0     0     0     0    -1     0     0     0     0        0            0          0  ]};
c.p{14}={'mp:css','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     0     1     0        0            0          0  ]};
c.p{15}={'mp:csg','F',         [0    0    0     0     0    0     0     0     0    -1     0     0     0     0     0     0        0            0          0  ]};
c.p{16}={'mp:cjd','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     1     0     0        0            0          0  ]};
c.p{17}={'mp:cjs','F',         [0    0    0     0     0    0     0     0     0     0     0     0     0     0     1     0        0            0          0  ]};
c.p{18}={'mp:fug','Hz',        [0    0    0     0     0    0     0     0     0     0     0     0     0     0     0     1        0            0          0  ]};
c.p{19}={'mp:gmoverid','V',    [0    0    0     0     0    0     0     0     0     0     0     0     0     0     0     0        1            0          0  ]};
c.p{20}={'mp:rout','Ohm',      [0    0    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            1          0  ]};
c.p{21}={'mp:vdsat','V',       [0    1    0     0     0    0     0     0     0     0     0     0     0     0     0     0        0            0         -1  ]};
% Noise Section
c.outvars_noise = {'STH','SFL'};
c.n_noise{1}= {'mn:id', ''};
c.n_noise{2}= {'mn:fn', ''};
%
c.p_noise{1}= {'mp:id', ''};
c.p_noise{2}= {'mp:fn', ''};


% Simulation netlist
netlist = sprintf([...
'//techsweep_180msrf.scs \n'...
'include  %s\n'...
'include "techsweep_params_180msrf.scs" \n'...
'save mn \n'...
'save mp \n'...
'parameters gs=0 ds=0 \n'...
'vnoi     (vx  0)         vsource dc=0  \n'...
'vdsn     (vdn vx)        vsource dc=ds  \n'...
'vgsn     (vgn 0)         vsource dc=gs  \n'...
'vbsn     (vbn 0)         vsource dc=-sb \n'...
'vdsp     (vdp vx)        vsource dc=-ds \n'...
'vgsp     (vgp 0)         vsource dc=-gs \n'...
'vbsp     (vbp 0)         vsource dc=sb  \n'...
'\n'...
'mn       (vdn vgn 0 vbn) %s  l=length*1e-6 w=%de-6 m=1 nf=%d \n'...
'mp       (vdp vgp 0 vbp) %s  l=length*1e-6 w=%de-6 m=1 nf=%d \n'...
'\n'...
'simOptions options gmin=1e-13 reltol=1e-4 vabstol=1e-6 iabstol=1e-10 temp=%d tnom=27 rawfmt=psfbin rawfile="./%s" \n'...
'sweepvds sweep param=ds start=0 stop=%d step=%d { \n'...
'   sweepvgs dc param=gs start=0 stop=%d step=%d \n'...
'}\n'...
'sweepvds_noise sweep param=ds start=0 stop=%d step=%d { \n'...
'   sweepvgs_noise noise freq=1 oprobe=vnoi param=gs start=0 stop=%d step=%d \n'...
'}\n'...
], c.modelfile, ...
c.modeln, c.WIDTH, c.NFING, ...
c.modelp, c.WIDTH, c.NFING, ...
c.temp-273, c.outfile, ...
c.VGS_max, c.VGS_step, ...
c.VDS_max, c.VDS_step, ...
c.VGS_max, c.VGS_step, ...
c.VDS_max, c.VDS_step);

% Write netlist
fid = fopen('techsweep_180msrf.scs', 'w');
fprintf(fid, netlist);
fclose(fid);

return



