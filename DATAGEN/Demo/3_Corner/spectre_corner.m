% Matlab script for technology characterization
% Boris Murmann, Stanford University
% Tested with MMSIM12.11.134
% September 12, 2017
% Updated by Fengqi Zhang, Columbia University
% 2019-08-01, 2020-05-04
% 1. Replace XXX_tech -> 180msrf

clearvars; 
close all;
% Time the run time
tic
% Load configuration
corner = ["tt","ff"];
%corner = ["ff"];
%corner = ["ss"];
%corner = ["fs"];
%corner = ["sf"];

for cSel = 1:length(corner)
  c = corner_bsim4_180msrf_spectre(corner(cSel));

  % Write sweep info
  nmos.INFO   = c.modelinfo;
  nmos.CORNER = c.corner;
  nmos.TEMP   = c.temp;
  nmos.NFING  = c.NFING;
  nmos.L      = c.LENGTH';
  nmos.W      = c.WIDTH;
  nmos.VGS    = c.VGS';
  nmos.VDS    = c.VDS';
  nmos.VSB    = c.VSB';
                                %
  pmos.INFO   = c.modelinfo;
  pmos.CORNER = c.corner;
  pmos.TEMP   = c.temp;
  pmos.NFING  = c.NFING;
  pmos.L      = c.LENGTH';
  pmos.W      = c.WIDTH;
  pmos.VGS    = c.VGS';
  pmos.VDS    = c.VDS';
  pmos.VSB    = c.VSB';

  % Simulation loop
  for i = 1:length(c.LENGTH)
    str=sprintf('Simulation Starts for L = %2.3f', c.LENGTH(i));
    disp(str);
    for j = 1:length(c.VSB)
                                % Write simulation parameters
      fid = fopen('techsweep_params_180msrf.scs', 'w');
      fprintf(fid,'parameters length = %d\n', c.LENGTH(i));
      fprintf(fid,'parameters sb = %d\n', c.VSB(j));
      fclose(fid);
      simStr = sprintf('Simulation Finished for L = %2.3f with VSB = %2.2f V', c.LENGTH(i), c.VSB(j));

      pause(2.5)

      % Run simulator
      [status,result] = system(c.simcmd);
      if(status)
        disp('Simulation did not run properly. Check techsweep.out.')
        return;
      else
        disp(simStr)
      end
      
                                % Initialize data blocks
      for m = 1:length(c.outvars)
        nmos.(c.outvars{m})(i,:,:,j) = zeros(length(c.VGS), length(c.VDS));
        pmos.(c.outvars{m})(i,:,:,j) = zeros(length(c.VGS), length(c.VDS));
      end
      
                                % Read and store results
      for k = 1:length(c.n)
        params_n = c.n{k};
        struct_n = cds_srr(c.outfile, c.sweep, params_n{1});
        values_n = struct_n.(params_n{2});
        params_p = c.p{k};
        struct_p = cds_srr(c.outfile, c.sweep, params_p{1});
        values_p = struct_p.(params_p{2});
        for m = 1:length(c.outvars)
          nmos.(c.outvars{m})(i,:,:,j)  = squeeze(nmos.(c.outvars{m})(i,:,:,j)) + values_n*params_n{3}(m);
          pmos.(c.outvars{m})(i,:,:,j)  = squeeze(pmos.(c.outvars{m})(i,:,:,j)) + values_p*params_p{3}(m);
        end
      end
                                % Noise results
      for k = 1:length(c.n_noise)
        params_n = c.n_noise{k};
                    % note: using cds_innersrr, since cds_srr is buggy for noise
        struct_n = cds_innersrr(c.outfile, c.sweep_noise, params_n{1},0);
        field_names = fieldnames(struct_n);
        values_n = struct_n.(field_names{4});
        params_p = c.p_noise{k};
                    % note: using cds_innersrr, since cds_srr is buggy for noise
        struct_p = cds_innersrr(c.outfile, c.sweep_noise, params_p{1},0);
        field_names = fieldnames(struct_p);
        values_p = struct_p.(field_names{4});
        nmos.(c.outvars_noise{k})(i,:,:,j) = squeeze(values_n);
        pmos.(c.outvars_noise{k})(i,:,:,j) = squeeze(values_p);
      end
    end
  end
  % Save the Data
  save(c.savefilen, '-struct', 'nmos', '-v7.3');
  save(c.savefilep, '-struct', 'pmos', '-v7.3');
end

toc

