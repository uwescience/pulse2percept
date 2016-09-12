function R4=ModelKrishnan(p, STIM, freqNum)
 STIM.freq = STIM.freqList(freqNum);
    sawtooth = STIM.freq*mod(STIM.t,1/STIM.freq);
    on  = sawtooth > STIM.pulsedur*STIM.freq & sawtooth < 2*STIM.pulsedur*STIM.freq;
    off = sawtooth < STIM.pulsedur*STIM.freq;
    STIM.tsform = on-off;
    
    % total charge in the system as a function of time
    chargeacc=STIM.tsample*cumsum(max(STIM.tsform,0));
    tmp = p.e*STIM.tsample*conv(p.G2,chargeacc);
    STIM.chargeacc = tmp(1:length(STIM.t));

    t2 = 0:STIM.tsample:.30;
p.G2k = Gamma(1, p.tau2k, t2);

% total charge in the system as a function of time
chargeacc=STIM.tsample*cumsum(max(STIM.tsform,0));
tmp = p.ek*STIM.tsample*conv(p.G2k,chargeacc);
STIM.chargeacc = tmp(1:length(STIM.t));

%convolve the stimulus with the ganglion cell impulse response
R1 = STIM.tsample.*conv(p.G1,STIM.tsform-STIM.chargeacc);
R1 = STIM.amp(freqNum).*R1(1:length(STIM.t)); %cut off end due to convolution

%% stationary nonlinearity
R3 = max(R1,0);
R3norm = R3 / max(R3);

scFac=p.asymptote./(1+exp(-(max(R3(:))-p.shift)./p.slope));
R3 = R3norm .* scFac ;

%% slow convolution

R4 =  STIM.tsample*conv(p.G3,R3);

R4 = R4(1:length(STIM.t));
end